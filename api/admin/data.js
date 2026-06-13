// Vercel Edge Function — Admin data endpoint
// Returns submissions + chat logs from Vercel KV
// Protected by ADMIN_SECRET env var (set same as your passphrase)

export const config = { runtime: 'edge' };

const ADMIN_SECRET = process.env.ADMIN_SECRET || 'shipfaster';
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

export default async function handler(req) {
  const url = new URL(req.url);
  const token = req.headers.get('x-admin-token') || url.searchParams.get('token');

  if (token !== ADMIN_SECRET) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'content-type': 'application/json' },
    });
  }

  const action = url.searchParams.get('action') || 'load';

  if (action === 'load') {
    const [submissions, chats, subCount, chatCount] = await Promise.all([
      kvGet('lofts:submissions'),
      kvGet('lofts:chats'),
      kvLen('lofts:submissions'),
      kvLen('lofts:chats'),
    ]);
    return new Response(JSON.stringify({
      submissions,
      chats,
      stats: {
        totalSubmissions: subCount,
        totalChats: chatCount,
      },
    }), { status: 200, headers: { 'content-type': 'application/json', 'Cache-Control': 'no-store' } });
  }

  if (action === 'clear' && req.method === 'POST') {
    const { type } = await req.json().catch(() => ({}));
    if (type === 'submissions') await kvDel('lofts:submissions');
    else if (type === 'chats') await kvDel('lofts:chats');
    return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'content-type': 'application/json' } });
  }

  return new Response(JSON.stringify({ error: 'Unknown action' }), { status: 400, headers: { 'content-type': 'application/json' } });
}
