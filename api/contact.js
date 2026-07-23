// Vercel Edge Function: validate and persist enquiries before notifications.
import { enrollLeadAutomation } from './_lib/automation.js';

export const config = { runtime: 'edge' };

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MAX_REQUEST_BYTES = 24000;

async function kvCmd(...args) {
  const url = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  if (!url || !token) throw new Error('Lead storage is unavailable.');
  const response = await fetch(url, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.error) throw new Error('Lead storage is unavailable.');
  return payload.result ?? null;
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', 'Cache-Control': 'no-store' },
  });
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[character]);
}

function cleanField(value, length = 4000) {
  return String(value || '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, length);
}

async function requestFingerprint(req) {
  const address = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim()
    || req.headers.get('x-real-ip')
    || 'unknown';
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`${address}:lofts-contact-v1`));
  return Array.from(new Uint8Array(digest)).slice(0, 12).map(byte => byte.toString(16).padStart(2, '0')).join('');
}

async function checkRateLimit(req) {
  const key = `lofts:contact:rate:${await requestFingerprint(req)}`;
  const count = Number(await kvCmd('INCR', key));
  if (count === 1) await kvCmd('EXPIRE', key, '600');
  return count <= 5;
}

async function parsePayload(req) {
  const contentLength = Number(req.headers.get('content-length') || 0);
  if (contentLength > MAX_REQUEST_BYTES) throw new Error('Request too large.');
  const contentType = req.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return req.json();
  const form = await req.formData();
  return Object.fromEntries([...form.entries()].map(([key, value]) => [key, typeof value === 'string' ? value : String(value)]));
}

async function notifyTeam(lead, subject) {
  const toEmail = process.env.CONTACT_EMAIL;
  const bccEmail = process.env.CONTACT_EMAIL_BCC;
  const resendKey = process.env.RESEND_API_KEY;
  if (!toEmail || !resendKey) return { ok: false, message: 'Notification service is not configured.' };
  const visible = Object.entries(lead).filter(([key]) => !key.startsWith('_') && key !== 'consentNotice');
  const text = visible.map(([key, value]) => `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}`).join('\n');
  const html = `<div style="font-family:Arial,sans-serif;max-width:640px;margin:0 auto;padding:24px;color:#1a1612">
    <h2 style="margin:0 0 16px;font-size:18px">${escapeHtml(subject)}</h2>
    <table style="width:100%;border-collapse:collapse">${visible.map(([key, value]) => `<tr><td style="padding:8px 12px;background:#f4f0ea;font-weight:600;width:30%;vertical-align:top;border:1px solid #e0d8ce">${escapeHtml(key.charAt(0).toUpperCase() + key.slice(1))}</td><td style="padding:8px 12px;border:1px solid #e0d8ce;vertical-align:top">${escapeHtml(value)}</td></tr>`).join('')}</table>
    <p style="margin:20px 0 0;font-size:12px;color:#777">Stored in Ads Command before this notification was sent.</p>
  </div>`;
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${resendKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: 'Lofts Studio <noreply@lofts.studio>',
        to: bccEmail ? [toEmail, bccEmail] : [toEmail],
        subject,
        html,
        text,
        reply_to: lead.email || undefined,
      }),
    });
    const payload = await response.json().catch(() => ({}));
    return { ok: response.ok, message: payload.message || '' };
  } catch {
    return { ok: false, message: 'Notification request failed.' };
  }
}

export default async function handler(req) {
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);

  let payload;
  try { payload = await parsePayload(req); } catch (error) { return json({ success: false, message: error.message || 'Invalid form data.' }, 400); }

  if (cleanField(payload._gotcha, 200)) return json({ success: true, message: 'Received' });
  const startedAt = Number(payload._startedAt || 0);
  if (startedAt && Date.now() - startedAt < 1800) return json({ success: false, message: 'Please wait a moment and try again.' }, 429);

  const source = cleanField(payload.source || 'contact-form', 100);
  const isNewsletter = source === 'footer-newsletter';
  const email = cleanField(payload.email, 254).toLowerCase();
  const name = cleanField(payload.name, 120);
  if (!EMAIL_PATTERN.test(email)) return json({ success: false, message: 'Enter a valid email address.' }, 400);
  if (!isNewsletter && name.length < 2) return json({ success: false, message: 'Enter your name.' }, 400);

  try {
    if (!await checkRateLimit(req)) return json({ success: false, message: 'Too many requests. Please try again in ten minutes.' }, 429);
  } catch {
    return json({ success: false, message: 'The enquiry could not be stored right now. Please email hi@lofts.studio.' }, 503);
  }

  const submissionId = cleanField(payload._submissionId, 96).replace(/[^a-zA-Z0-9-]/g, '') || crypto.randomUUID();
  try {
    const first = await kvCmd('SET', `lofts:contact:submission:${submissionId}`, '1', 'NX', 'EX', '86400');
    if (!first) return json({ success: true, message: 'Already received' });
  } catch {
    return json({ success: false, message: 'The enquiry could not be stored right now. Please email hi@lofts.studio.' }, 503);
  }

  const clean = {};
  for (const [key, value] of Object.entries(payload)) {
    if (key.startsWith('_') || ['consentNotice', 'trackingConsent'].includes(key)) continue;
    clean[key] = cleanField(value);
  }
  clean.email = email;
  clean.name = name;
  clean.source = source;
  clean.nurtureConsent = String(payload.nurtureConsent || '').toLowerCase() === 'yes' ? 'yes' : 'no';

  const lead = {
    ...clean,
    country: cleanField(req.headers.get('x-vercel-ip-country'), 2).toUpperCase(),
    consentNotice: isNewsletter
      ? 'newsletter-subscription-v1'
      : 'project-enquiry-followup-v1: relevant follow-ups with opt-out; day 60/90 only when nurtureConsent=yes',
    trackingConsent: 'no',
    _id: submissionId,
    _projectId: 'lofts-studio',
    _ts: Date.now(),
  };
  const subject = cleanField(payload._subject, 180) || (isNewsletter
    ? `New subscriber - ${email}`
    : 'New lead - Lofts Studio');
  lead._subject = subject;

  try {
    await kvCmd('LPUSH', 'lofts:submissions', JSON.stringify(lead));
  } catch {
    return json({ success: false, message: 'The enquiry could not be stored right now. Please email hi@lofts.studio.' }, 503);
  }

  const notification = await notifyTeam(lead, subject);
  let automation = null;
  if (!isNewsletter) {
    try { automation = await enrollLeadAutomation(lead, new URL(req.url).origin); } catch { automation = null; }
  }

  return json({
    success: true,
    message: 'Received',
    submissionId,
    notification: notification.ok ? 'sent' : 'delayed',
    automation: automation?.status || 'not-enrolled',
  });
}
