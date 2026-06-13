// Vercel Edge Function — sends contact/subscriber emails via Resend
// and stores a copy in Vercel KV for the admin inbox.
//
// Required env vars (Vercel project Settings → Environment Variables):
//   RESEND_API_KEY  — Resend API key (re_...)
//   CONTACT_EMAIL   — destination address (hi@lofts.studio)

export const config = { runtime: 'edge' };

async function kvStore(payload) {
  const KV_URL   = process.env.KV_REST_API_URL;
  const KV_TOKEN = process.env.KV_REST_API_TOKEN;
  if (!KV_URL || !KV_TOKEN) return;
  try {
    await fetch(KV_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(['LPUSH', 'lofts:submissions', JSON.stringify({ ...payload, _ts: Date.now() })]),
    });
  } catch { /* non-blocking */ }
}

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'POST only' }), { status: 405 });
  }

  const toEmail     = process.env.CONTACT_EMAIL;
  const resendKey   = process.env.RESEND_API_KEY;

  if (!toEmail || !resendKey) {
    return new Response(JSON.stringify({
      success: false,
      message: 'Contact endpoint is not configured.',
    }), { status: 500, headers: { 'content-type': 'application/json' } });
  }

  // Parse payload
  let payload = {};
  try {
    const ct = req.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      payload = await req.json();
    } else {
      const form = await req.formData();
      for (const [k, v] of form.entries()) payload[k] = typeof v === 'string' ? v : String(v);
    }
  } catch { payload = {}; }

  // Sanitize
  const clean = {};
  for (const [k, v] of Object.entries(payload)) {
    if (k.startsWith('_')) continue;
    clean[k] = String(v).slice(0, 4000);
  }

  const source  = clean.source || 'contact-form';
  const subject = payload._subject || (source === 'footer-newsletter'
    ? `New subscriber — ${clean.email || 'unknown'}`
    : `New lead — Lofts Studio`);

  // Build plain-text email body from all submitted fields
  const fields = Object.entries(clean)
    .filter(([k]) => k !== 'source')
    .map(([k, v]) => `${k.charAt(0).toUpperCase() + k.slice(1)}: ${v}`)
    .join('\n');

  const htmlBody = `
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1a1612;">
      <h2 style="margin:0 0 16px;font-size:18px;">${subject}</h2>
      <table style="width:100%;border-collapse:collapse;">
        ${Object.entries(clean).filter(([k]) => k !== 'source').map(([k, v]) => `
        <tr>
          <td style="padding:8px 12px;background:#f4f0ea;font-weight:600;width:30%;vertical-align:top;border:1px solid #e0d8ce;">
            ${k.charAt(0).toUpperCase() + k.slice(1)}
          </td>
          <td style="padding:8px 12px;border:1px solid #e0d8ce;vertical-align:top;">${v}</td>
        </tr>`).join('')}
        <tr>
          <td style="padding:8px 12px;background:#f4f0ea;font-weight:600;border:1px solid #e0d8ce;">Source</td>
          <td style="padding:8px 12px;border:1px solid #e0d8ce;">${source}</td>
        </tr>
      </table>
      <p style="margin:20px 0 0;font-size:12px;color:#999;">Sent via lofts.studio</p>
    </div>`;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${resendKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Lofts Studio <onboarding@resend.dev>',
        to:   [toEmail],
        subject,
        html: htmlBody,
        text: fields,
        reply_to: clean.email || undefined,
      }),
    });

    const data = await r.json().catch(() => ({}));
    const success = r.ok;

    // Store in KV regardless
    await kvStore({ ...clean, _subject: subject, source });

    return new Response(JSON.stringify({ success, message: success ? 'Sent' : (data.message || 'Failed') }),
      { status: 200, headers: { 'content-type': 'application/json' } });

  } catch (e) {
    return new Response(JSON.stringify({ success: false, message: 'Network blip — please try again.' }),
      { status: 200, headers: { 'content-type': 'application/json' } });
  }
}
