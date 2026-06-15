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
// Moderated by default — new comments are held until approved in /admin/comments.html.
// Set COMMENTS_MODERATION="0" to auto-publish instead.
const MODERATED = process.env.COMMENTS_MODERATION !== '0';
// Server-side secret for admin approve/delete (set in Vercel env).
const ADMIN_TOKEN = process.env.COMMENTS_ADMIN_TOKEN || '';
// Email notifications (reuses the contact form's Resend setup).
const RESEND_KEY = process.env.RESEND_API_KEY;
const NOTIFY_TO  = process.env.CONTACT_EMAIL;
const SITE       = process.env.SITE_URL || 'https://lofts.studio';

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

// Notify the studio inbox when a comment comes in (non-blocking, best-effort).
async function notify(slug, name, email, body) {
  if (!RESEND_KEY || !NOTIFY_TO) return;
  const postUrl = `${SITE}/blog/${slug}.html#comments`;
  const modUrl  = `${SITE}/admin/comments.html`;
  const subject = MODERATED ? `New comment awaiting review — ${slug}` : `New comment — ${slug}`;
  const html = `
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1a1612;">
      <h2 style="margin:0 0 4px;font-size:18px;">${MODERATED ? 'Comment awaiting review' : 'New comment'}</h2>
      <p style="margin:0 0 16px;color:#6c6258;font-size:13px;">on <a href="${postUrl}">${esc(slug)}</a></p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <tr><td style="padding:8px 12px;background:#f4f0ea;font-weight:600;width:90px;border:1px solid #e0d8ce;">Name</td><td style="padding:8px 12px;border:1px solid #e0d8ce;">${esc(name)}</td></tr>
        ${email ? `<tr><td style="padding:8px 12px;background:#f4f0ea;font-weight:600;border:1px solid #e0d8ce;">Email</td><td style="padding:8px 12px;border:1px solid #e0d8ce;">${esc(email)}</td></tr>` : ''}
        <tr><td style="padding:8px 12px;background:#f4f0ea;font-weight:600;vertical-align:top;border:1px solid #e0d8ce;">Comment</td><td style="padding:8px 12px;border:1px solid #e0d8ce;white-space:pre-wrap;">${esc(body)}</td></tr>
      </table>
      <p style="margin:20px 0 0;">
        <a href="${modUrl}" style="display:inline-block;background:#1a1612;color:#fff;text-decoration:none;padding:10px 18px;border-radius:8px;font-size:14px;">${MODERATED ? 'Review &amp; approve' : 'Open moderation'}</a>
      </p>
    </div>`;
  try {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${RESEND_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: 'Lofts Studio <noreply@lofts.studio>',
        to: [NOTIFY_TO],
        subject,
        html,
        text: `${name} commented on ${slug}:\n\n${body}\n\n${MODERATED ? 'Review & approve' : 'Moderate'}: ${modUrl}`,
        reply_to: email || undefined,
      }),
    });
  } catch { /* non-blocking */ }
}

function isAdmin(req) {
  if (!ADMIN_TOKEN) return false;
  const tok = req.headers.get('x-admin-token') || '';
  // constant-time-ish compare
  if (tok.length !== ADMIN_TOKEN.length) return false;
  let diff = 0;
  for (let i = 0; i < tok.length; i++) diff |= tok.charCodeAt(i) ^ ADMIN_TOKEN.charCodeAt(i);
  return diff === 0;
}

// Find a comment by id in its per-slug list and update it (return new object),
// or delete it (return null from mutate).
async function findAndMutate(slug, id, mutate) {
  const key = `comments:${slug}`;
  const arr = (await kv(['LRANGE', key, '0', '-1'])) || [];
  for (let i = 0; i < arr.length; i++) {
    let c;
    try { c = typeof arr[i] === 'string' ? JSON.parse(arr[i]) : arr[i]; } catch { continue; }
    if (c && c.id === id) {
      const nv = mutate(c);
      if (nv === null) {
        await kv(['LSET', key, String(i), '__DELETED__']);
        await kv(['LREM', key, '1', '__DELETED__']);
      } else {
        await kv(['LSET', key, String(i), JSON.stringify(nv)]);
      }
      return true;
    }
  }
  return false;
}

export default async function handler(req) {
  const url = new URL(req.url);

  // ── Admin: list every comment (incl. pending) for moderation ────
  if (req.method === 'GET' && url.searchParams.get('admin')) {
    if (!isAdmin(req)) return json({ ok: false, message: 'Unauthorized' }, 401);
    const slugs = (await kv(['SMEMBERS', 'comments:index'])) || [];
    const out = [];
    for (const s of slugs) {
      const raw = (await kv(['LRANGE', `comments:${s}`, '0', '-1'])) || [];
      for (const item of raw) {
        try {
          const c = typeof item === 'string' ? JSON.parse(item) : item;
          out.push({ id: c.id, slug: s, name: c.name, body: c.body, ts: c.ts, approved: c.approved !== false, email: c._email || '' });
        } catch { /* skip */ }
      }
    }
    out.sort((a, b) => b.ts - a.ts);
    return json({ ok: true, comments: out });
  }

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

  // ── Admin moderation actions ────────────────────────────────────
  if (p.action === 'approve' || p.action === 'delete') {
    if (!isAdmin(req)) return json({ ok: false, message: 'Unauthorized' }, 401);
    const aslug = cleanSlug(p.slug);
    if (!aslug || !p.id) return json({ ok: false, message: 'Missing slug or id.' }, 400);
    const done = await findAndMutate(aslug, p.id, p.action === 'delete' ? () => null : (c) => ({ ...c, approved: true }));
    return json({ ok: done });
  }

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

  await kv(['SADD', 'comments:index', slug]);            // track slugs for the moderation view
  await kv(['LPUSH', `comments:${slug}`, JSON.stringify(comment)]);
  await kv(['LTRIM', `comments:${slug}`, '0', String(KEEP - 1)]);
  await notify(slug, name, p.email || '', body);          // email the studio inbox

  return json({
    ok: true,
    pending: MODERATED,
    comment: MODERATED ? null : { id: comment.id, name: comment.name, body: comment.body, ts: comment.ts },
    message: MODERATED ? 'Thanks — your comment will appear once approved.' : 'Posted — thanks for adding to the conversation.',
  });
}
