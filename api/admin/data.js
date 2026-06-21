// Vercel Edge Function — Admin data endpoint
// Returns submissions + chat logs from Vercel KV
// Protected by ADMIN_SECRET env var (set same as your passphrase)

export const config = { runtime: 'edge' };

const ADMIN_SECRET = process.env.ADMIN_SECRET;
const KV_URL       = process.env.KV_REST_API_URL;
const KV_TOKEN     = process.env.KV_REST_API_TOKEN;

async function kvCmd(...args) {
  if (!KV_URL || !KV_TOKEN) return null;
  const res = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  if (!res.ok) return null;
  const json = await res.json();
  return json.result ?? null;
}

async function kvGet(key, start = 0, end = 199) {
  const result = await kvCmd('LRANGE', key, start, end);
  if (!Array.isArray(result)) return [];
  return result.map(item => {
    try { return JSON.parse(item); } catch { return item; }
  });
}

async function kvLen(key) {
  const result = await kvCmd('LLEN', key);
  return result || 0;
}

async function kvDel(key) {
  await kvCmd('DEL', key);
}

async function kvCommentIndex() {
  const result = await kvCmd('SMEMBERS', 'comments:index');
  return Array.isArray(result) ? result : [];
}

async function kvComments(limitPerPost = 120) {
  const slugs = await kvCommentIndex();
  const comments = [];
  for (const slug of slugs) {
    const raw = await kvGet(`comments:${slug}`, 0, limitPerPost - 1);
    for (const item of raw) {
      if (!item || typeof item !== 'object') continue;
      comments.push({
        id: item.id,
        slug,
        name: item.name,
        body: item.body,
        ts: item.ts,
        approved: item.approved !== false,
        email: item._email || '',
      });
    }
  }
  comments.sort((a, b) => (b.ts || 0) - (a.ts || 0));
  return comments;
}

async function mutateComment(slug, id, mutate) {
  const key = `comments:${slug}`;
  const raw = await kvCmd('LRANGE', key, '0', '-1');
  if (!Array.isArray(raw)) return false;
  for (let i = 0; i < raw.length; i++) {
    let comment;
    try { comment = typeof raw[i] === 'string' ? JSON.parse(raw[i]) : raw[i]; } catch { continue; }
    if (!comment || comment.id !== id) continue;
    const next = mutate(comment);
    if (next === null) {
      await kvCmd('LSET', key, String(i), '__DELETED__');
      await kvCmd('LREM', key, '1', '__DELETED__');
    } else {
      await kvCmd('LSET', key, String(i), JSON.stringify(next));
    }
    return true;
  }
  return false;
}

export default async function handler(req) {
  const url = new URL(req.url);
  const token = req.headers.get('x-admin-token') || url.searchParams.get('token');

  if (!ADMIN_SECRET || token !== ADMIN_SECRET) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'content-type': 'application/json' },
    });
  }

  const action = url.searchParams.get('action') || 'load';

  if (action === 'load') {
    const [submissions, chats, comments, subCount, chatCount] = await Promise.all([
      kvGet('lofts:submissions'),
      kvGet('lofts:chats'),
      kvComments(),
      kvLen('lofts:submissions'),
      kvLen('lofts:chats'),
    ]);
    const pendingComments = comments.filter(c => !c.approved).length;
    return new Response(JSON.stringify({
      submissions,
      chats,
      comments,
      stats: {
        totalSubmissions: subCount,
        totalChats: chatCount,
        totalComments: comments.length,
        pendingComments,
        approvedComments: comments.length - pendingComments,
      },
    }), { status: 200, headers: { 'content-type': 'application/json', 'Cache-Control': 'no-store' } });
  }

  if (action === 'comment' && req.method === 'POST') {
    const { type, slug, id } = await req.json().catch(() => ({}));
    const cleanSlug = String(slug || '').toLowerCase().replace(/[^a-z0-9\-]/g, '').slice(0, 80);
    if (!cleanSlug || !id) {
      return new Response(JSON.stringify({ ok: false, error: 'Missing comment id or slug.' }), {
        status: 400,
        headers: { 'content-type': 'application/json' },
      });
    }
    const ok = type === 'delete'
      ? await mutateComment(cleanSlug, id, () => null)
      : await mutateComment(cleanSlug, id, c => ({ ...c, approved: true }));
    return new Response(JSON.stringify({ ok }), {
      status: ok ? 200 : 404,
      headers: { 'content-type': 'application/json', 'Cache-Control': 'no-store' },
    });
  }

  if (action === 'clear' && req.method === 'POST') {
    const { type } = await req.json().catch(() => ({}));
    if (type === 'submissions') await kvDel('lofts:submissions');
    else if (type === 'chats') await kvDel('lofts:chats');
    return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'content-type': 'application/json' } });
  }

  return new Response(JSON.stringify({ error: 'Unknown action' }), { status: 400, headers: { 'content-type': 'application/json' } });
}
