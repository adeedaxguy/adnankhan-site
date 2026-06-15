// Vercel Edge Function — blog comments, backed by Vercel KV (Upstash REST).
//
// GET  /api/comments?slug=<post-slug>      -> { ok, comments: [{id,name,body,ts}] }
// POST /api/comments  { slug,name,email,body,hp_url,t }  -> { ok, comment } | { ok:false,message }
//
// Spam protection (no third party, no captcha friction):
//   • Honeypot field (hp_url) — bots fill it; we silently discard.
//   • Time-trap — submissions faster than MIN_SECONDS are rejected.
//   • Per-IP rate limit (KV counter w/ TTL).
//   • Link cap, length caps, banned-word + gibberish heuristics.
//   • All output HTML-escaped before storage and render (XSS-safe).
//
// Env vars (Vercel → Settings → Environment Variables):
//   KV_REST_API_URL, KV_REST_API_TOKEN  (already used by the contact form)
//   COMMENTS_MODERATION = "1"  (optional) -> hold new comments until approved

export const config = { runtime: 'edge' };

const MIN_SECONDS   = 4;      // a human takes longer than this to write + submit
const MAX_BODY      = 3000;
const MAX_NAME      = 60;
const MAX_LINKS     = 2;
const RATE_MAX      = 6;      // comments per IP per hour
const KEEP          = 500;    // max stored comments per post
const RETURN_MAX    = 200;

const KV_URL   = process.env.KV_REST_API_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN;
const MODERATED = process.env.COMMENTS_MODERATION === '1';

const BANNED = /(viagra|cialis|casino|porn|sex cam|payday loan|crypto pump|\bseo services\b|telegram\.me|bit\.ly\/|escort|loan offer|\bnsfw\b|онлайн|кредит)/i;

async function kv(command) {
  if (!KV_URL || !KV_TOKEN) return null;
  const r = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(command),
  });
  if (!r.ok) return null;
  const data = await r.json().catch(() => ({}));
  return data.result;
}

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function cleanSlug(s) {
  return String(s || '').toLowerCase().replace(/[^a-z0-9\-]/g, '').slice(0, 80);
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
  });
}

export default async function handler(req) {
  const url = new URL(req.url);

  // ── List comments ───────────────────────────────────────────────
  if (req.method === 'GET') {
    const slug = cleanSlug(url.searchParams.get('slug'));
    if (!slug) return json({ ok: false, comments: [] }, 400);
    const raw = (await kv(['LRANGE', `comments:${slug}`, '0', String(RETURN_MAX - 1)])) || [];
    const comments = [];
    for (const item of raw) {
      try {
        const c = typeof item === 'string' ? JSON.parse(item) : item;
        if (c && c.approved !== false) {
          comments.push({ id: c.id, name: c.name, body: c.body, ts: c.ts });
        }
      } catch { /* skip */ }
    }
    return json({ ok: true, comments });
  }

  if (req.method !== 'POST') return json({ ok: false, message: 'Method not allowed' }, 405);

  // ── Create comment ──────────────────────────────────────────────
  let p = {};
  try { p = await req.json(); } catch { return json({ ok: false, message: 'Bad request' }, 400); }

  const slug = cleanSlug(p.slug);
  if (!slug) return json({ ok: false, message: 'Missing post.' }, 400);

  // Honeypot — pretend success, store nothing.
  if (p.hp_url) return json({ ok: true, discarded: true });

  // Time-trap.
  const elapsed = Number(p.t) || 0;
  if (elapsed > 0 && elapsed < MIN_SECONDS * 1000) {
    return json({ ok: false, message: 'That was a little too quick — give it a moment and try again.' }, 429);
  }

  const name = String(p.name || '').trim().replace(/\s+/g, ' ').slice(0, MAX_NAME);
  const body = String(p.body || '').trim().replace(/\r/g, '').replace(/\n{3,}/g, '\n\n').slice(0, MAX_BODY);

  if (name.length < 2)  return json({ ok: false, message: 'Please add your name.' }, 400);
  if (body.length < 2)  return json({ ok: false, message: 'Please write a comment.' }, 400);

  // Content heuristics.
  const links = (body.match(/https?:\/\/|www\./gi) || []).length;
  if (links > MAX_LINKS) return json({ ok: false, message: 'Too many links — please keep it to two or fewer.' }, 400);
  if (BANNED.test(body) || BANNED.test(name)) return json({ ok: false, message: 'That comment looks like spam.' }, 400);
  const letters = (body.match(/[a-z]/gi) || []).length;
  const caps = (body.match(/[A-Z]/g) || []).length;
  if (letters > 20 && caps / letters > 0.6) return json({ ok: false, message: 'Please don’t write in all caps.' }, 400);
  if (/(.)\1{9,}/.test(body)) return json({ ok: false, message: 'That comment looks like spam.' }, 400);

  // Per-IP rate limit.
  const ip = (req.headers.get('x-forwarded-for') || '').split(',')[0].trim() || 'anon';
  const rlKey = `rl:comments:${ip}`;
  const count = await kv(['INCR', rlKey]);
  if (count === 1) await kv(['EXPIRE', rlKey, '3600']);
  if (typeof count === 'number' && count > RATE_MAX) {
    return json({ ok: false, message: 'You’ve posted a few times already — try again later.' }, 429);
  }

  if (!KV_URL || !KV_TOKEN) {
    return json({ ok: false, message: 'Comments aren’t available right now.' }, 503);
  }

  const comment = {
    id: (crypto.randomUUID && crypto.randomUUID()) || String(Date.now()) + Math.random().toString(36).slice(2),
    name: esc(name),
    body: esc(body),
    ts: Date.now(),
    approved: !MODERATED,
  };
  if (p.email) comment._email = esc(String(p.email).slice(0, 120)); // stored privately, never returned

  await kv(['LPUSH', `comments:${slug}`, JSON.stringify(comment)]);
  await kv(['LTRIM', `comments:${slug}`, '0', String(KEEP - 1)]);

  return json({
    ok: true,
    pending: MODERATED,
    comment: MODERATED ? null : { id: comment.id, name: comment.name, body: comment.body, ts: comment.ts },
    message: MODERATED ? 'Thanks — your comment will appear once approved.' : 'Posted — thanks for adding to the conversation.',
  });
}
