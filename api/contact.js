// Vercel Edge Function — proxies contact form submissions to Formsubmit
// and stores a copy in Vercel KV for the admin inbox.
//
// Set CONTACT_EMAIL in Vercel project Settings → Environment Variables.
// (already set in production; this Edge Function reads it server-side only.)

export const config = { runtime: 'edge' };

async function kvStore(payload) {
  const KV_URL   = process.env.KV_REST_API_URL;
  const KV_TOKEN = process.env.KV_REST_API_TOKEN;
  if (!KV_URL || !KV_TOKEN) return;
  try {
    // Upstash REST API: POST to base URL with ["COMMAND", "key", "value"] body
    await fetch(KV_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(['LPUSH', 'lofts:submissions', JSON.stringify({ ...payload, _ts: Date.now() })]),
    });
  } catch { /* non-blocking — don't fail the form submit */ }
}

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'POST only' }), { status: 405 });
  }

  const email = process.env.CONTACT_EMAIL;
  if (!email) {
    return new Response(JSON.stringify({
      success: false,
      message: "Contact endpoint is not configured. Try the chat widget bottom-right."
    }), { status: 500, headers: { 'content-type': 'application/json' } });
  }

  // Forward the original form payload to Formsubmit
  let payload = {};
  try {
    const ct = req.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      payload = await req.json();
    } else {
      // multipart/form-data or x-www-form-urlencoded
      const form = await req.formData();
      for (const [k, v] of form.entries()) payload[k] = typeof v === 'string' ? v : String(v);
    }
  } catch {
    payload = {};
  }

  // Sanitize the payload — strip any user-supplied _ control keys
  const clean = {};
  for (const [k, v] of Object.entries(payload)) {
    if (k.startsWith('_')) continue; // we set our own control fields
    clean[k] = String(v).slice(0, 4000);
  }

  const ccEmail = process.env.CONTACT_EMAIL_CC;
  const body = new URLSearchParams({
    ...clean,
    _subject: payload._subject || 'New lead — Adnan K. Studio site',
    _captcha: 'false',
    _template: 'table',
    ...(ccEmail ? { _cc: ccEmail } : {}),
  });

  try {
    const r = await fetch(`https://formsubmit.co/ajax/${encodeURIComponent(email)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
      },
      body: body.toString(),
    });
    const data = await r.json().catch(() => ({ success: 'false' }));
    const success = data.success === 'true' || data.success === true || r.ok;
    // Store in KV regardless of formsubmit result (non-blocking)
    await kvStore({ ...clean, _subject: payload._subject || 'New lead', source: clean.source || 'contact-form' });
    return new Response(JSON.stringify({
      success,
      message: data.message || (r.ok ? 'Sent' : 'Failed'),
    }), { status: 200, headers: { 'content-type': 'application/json' } });
  } catch (e) {
    return new Response(JSON.stringify({
      success: false,
      message: 'Network blip — please try again in a moment.',
    }), { status: 200, headers: { 'content-type': 'application/json' } });
  }
}
