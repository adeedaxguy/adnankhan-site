// Vercel Edge Function: validate and persist enquiries before notifications.
import { enrollLeadAutomation, normalizeTimeZone, sendInboundReply } from './_lib/automation.js';
import { sendZohoEmail } from './_lib/zoho.js';

export const config = { runtime: 'edge' };

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MAX_REQUEST_BYTES = 24000;
const TURNSTILE_ACTION = 'lofts_lead';
const OUTBOX_KEY = 'lofts:contact:outbox';
const NOTIFICATION_RECIPIENTS = ['hi@lofts.studio', 'adnan.webexpert@gmail.com', 'adnan.toprated@gmail.com'];

async function verifyTurnstile(req, payload) {
  const secret = process.env.TURNSTILE_SECRET_KEY;
  if (!secret) return { status: 503, message: 'Verification is temporarily unavailable. Please email hi@lofts.studio.' };
  const token = cleanField(payload['cf-turnstile-response'], 2048);
  if (!token) return { status: 400, message: 'Please complete the human verification and try again.' };

  try {
    const body = new URLSearchParams({ secret, response: token });
    const remoteIp = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim();
    if (remoteIp) body.set('remoteip', remoteIp);
    const response = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
      signal: AbortSignal.timeout(8000),
    });
    if (!response.ok) throw new Error('Turnstile is unavailable.');
    const result = await response.json();
    if (!result.success || result.action !== TURNSTILE_ACTION || !['lofts.studio', 'www.lofts.studio'].includes(result.hostname)) {
      return { status: 400, message: 'Human verification failed or expired. Please try again.' };
    }
    return null;
  } catch {
    return { status: 503, message: 'Verification is temporarily unavailable. Please try again in a minute.' };
  }
}

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

function isFictionalNorthAmericanPhone(value) {
  const digits = String(value || '').replace(/\D/g, '');
  const local = digits.length === 11 && digits.startsWith('1') ? digits.slice(1) : digits;
  return /^[2-9]\d{2}55501\d{2}$/.test(local);
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

async function notifyTeam(lead, subject, trackDelivery = true) {
  const visible = Object.entries(lead).filter(([key]) => !key.startsWith('_') && key !== 'consentNotice');
  const text = visible.map(([key, value]) => `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}`).join('\n');
  const html = `<div style="font-family:Arial,sans-serif;max-width:640px;margin:0 auto;padding:24px;color:#1a1612">
    <h2 style="margin:0 0 16px;font-size:18px">${escapeHtml(subject)}</h2>
    <table style="width:100%;border-collapse:collapse">${visible.map(([key, value]) => `<tr><td style="padding:8px 12px;background:#f4f0ea;font-weight:600;width:30%;vertical-align:top;border:1px solid #e0d8ce">${escapeHtml(key.charAt(0).toUpperCase() + key.slice(1))}</td><td style="padding:8px 12px;border:1px solid #e0d8ce;vertical-align:top">${escapeHtml(value)}</td></tr>`).join('')}</table>
    <p style="margin:20px 0 0;font-size:12px;color:#777">Stored in Ads Command before this notification was sent.</p>
  </div>`;
  await Promise.all(NOTIFICATION_RECIPIENTS.map(async toAddress => {
    if (!trackDelivery) {
      try { await sendZohoEmail(lead._projectId, { toAddress, subject, htmlContent: html, content: text }); } catch { /* The lead remains saved in the CRM. */ }
      return;
    }
    const statusKey = `lofts:contact:delivery:${lead._id}`;
    const field = `notification:${toAddress}`;
    const status = await kvCmd('HGET', statusKey, field);
    if (['sent', 'sending', 'needs-review'].includes(status)) return;
    await kvCmd('HSET', statusKey, field, 'sending');
    try {
      await sendZohoEmail(lead._projectId, { toAddress, subject, htmlContent: html, content: text });
      await kvCmd('HSET', statusKey, field, 'sent');
    } catch {
      // An ambiguous provider failure must not produce a duplicate owner email.
      await kvCmd('HSET', statusKey, field, 'needs-review');
    }
  }));
}

async function forwardToGrowthOs(lead) {
  const endpoint = process.env.GROWTH_OS_INQUIRY_URL;
  if (!endpoint) return { ok: false, status: 'not-configured' };
  const detail = cleanField([lead.focus || lead.bottleneck, lead.message || lead.project || lead.details].filter(Boolean).join('\n') || Object.entries(lead).filter(([key]) => !key.startsWith('_') && !['name', 'email', 'source'].includes(key)).map(([key, value]) => `${key}: ${value}`).join('\n'), 3000);
  if (detail.length < 20) return { ok: false, status: 'insufficient-context' };
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { Origin: 'https://lofts.studio', 'Content-Type': 'application/json', 'Idempotency-Key': `lofts-${lead._id}` },
      signal: AbortSignal.timeout(8000),
      body: JSON.stringify({
        name: lead.name,
        email: lead.email,
        phone: lead.phone,
        company: cleanField(lead.company || lead.business || lead.website || 'Inbound project inquiry', 180),
        website: /^https?:\/\//i.test(String(lead.website || '')) ? lead.website : '',
        message: detail,
        consent: true,
        source: lead.source || 'lofts_site_inquiry',
        attribution: {
          country: lead.country || null,
          landing_page: lead.landingPage || lead.page || null,
          referrer: lead.referrer || null,
          utm_source: lead.utm_source || null,
          utm_medium: lead.utm_medium || null,
          utm_campaign: lead.utm_campaign || null,
        },
      }),
    });
    return { ok: response.ok, status: response.ok ? 'forwarded' : 'delayed' };
  } catch {
    return { ok: false, status: 'delayed' };
  }
}

async function processContactWork(submissionId) {
  const lockKey = `lofts:contact:work-lock:${submissionId}`;
  if (!await kvCmd('SET', lockKey, '1', 'NX', 'EX', '300')) return;
  try {
    const raw = await kvCmd('HGET', OUTBOX_KEY, submissionId);
    if (!raw) return;
    const { lead, subject, origin } = JSON.parse(raw);
    const tasks = [notifyTeam(lead, subject)];
    if (lead.source !== 'footer-newsletter') {
      tasks.push((async () => {
        const sequence = await enrollLeadAutomation(lead, origin, { deferFirstReply: true });
        const reply = await sendInboundReply(sequence);
        await kvCmd('HSET', `lofts:contact:delivery:${submissionId}`, 'reply', reply.status);
      })());
      tasks.push((async () => {
        const result = await forwardToGrowthOs(lead);
        await kvCmd('HSET', `lofts:contact:delivery:${submissionId}`, 'growthOs', result.status);
      })());
    }
    const results = await Promise.allSettled(tasks);
    if (results.every(result => result.status === 'fulfilled')) {
      await kvCmd('HDEL', OUTBOX_KEY, submissionId);
    } else {
      console.warn('Contact follow-up remains queued for retry:', submissionId);
    }
  } finally {
    await kvCmd('DEL', lockKey);
  }
}

export async function processPendingContacts(limit = 20) {
  const entries = await kvCmd('HGETALL', OUTBOX_KEY) || [];
  const ids = Array.isArray(entries)
    ? entries.filter((_, index) => index % 2 === 0).slice(0, limit)
    : Object.keys(entries).slice(0, limit);
  const results = await Promise.allSettled(ids.map(processContactWork));
  return { checked: ids.length, errors: results.filter(result => result.status === 'rejected').length };
}

export default async function handler(req, context) {
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
  const phone = cleanField(payload.phone, 32);
  if (!EMAIL_PATTERN.test(email)) return json({ success: false, message: 'Enter a valid email address.' }, 400);
  if (!isNewsletter && name.length < 2) return json({ success: false, message: 'Enter your name.' }, 400);
  if (!isNewsletter && /(?:https?:\/\/|www\.|\b[a-z0-9-]+\.(?:com|net|org|io|co|info|biz)(?:\/|\b))/i.test(name)) {
    return json({ success: false, message: 'Enter your name, without a website link.' }, 400);
  }
  if (!isNewsletter && (phone.replace(/\D/g, '').length < 7 || phone.replace(/\D/g, '').length > 15 || !/^[+\d\s().-]+$/.test(phone) || isFictionalNorthAmericanPhone(phone))) {
    return json({ success: false, message: 'Enter a valid phone or WhatsApp number, including your country code.' }, 400);
  }

  const submissionId = cleanField(payload._submissionId, 96).replace(/[^a-zA-Z0-9-]/g, '') || crypto.randomUUID();
  const submissionKey = `lofts:contact:submission:${submissionId}`;
  try {
    const [allowed, existing] = await Promise.all([checkRateLimit(req), kvCmd('GET', submissionKey)]);
    if (!allowed) return json({ success: false, message: 'Too many requests. Please try again in ten minutes.' }, 429);
    if (existing) return json({ success: true, message: 'Already received' });
  } catch {
    return json({ success: false, message: 'The enquiry could not be stored right now. Please email hi@lofts.studio.' }, 503);
  }

  const verificationError = await verifyTurnstile(req, payload);
  if (verificationError) return json({ success: false, message: verificationError.message }, verificationError.status);

  try {
    const first = await kvCmd('SET', submissionKey, '1', 'NX', 'EX', '86400');
    if (!first) return json({ success: true, message: 'Already received' });
  } catch {
    return json({ success: false, message: 'The enquiry could not be stored right now. Please email hi@lofts.studio.' }, 503);
  }

  const clean = {};
  for (const [key, value] of Object.entries(payload)) {
    if (key.startsWith('_') || ['consentNotice', 'trackingConsent', 'cf-turnstile-response'].includes(key)) continue;
    clean[key] = cleanField(value);
  }
  clean.email = email;
  clean.name = name;
  if (!isNewsletter) clean.phone = phone;
  const timezone = !isNewsletter && normalizeTimeZone(payload.timezone);
  if (timezone) clean.timezone = timezone;
  else delete clean.timezone;
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
    try { await kvCmd('DEL', submissionKey); } catch { /* The original storage failure is still reported. */ }
    return json({ success: false, message: 'The enquiry could not be stored right now. Please email hi@lofts.studio.' }, 503);
  }

  try {
    await kvCmd('HSET', OUTBOX_KEY, submissionId, JSON.stringify({ lead, subject, origin: new URL(req.url).origin }));
  } catch {
    // The lead is saved already; do not acknowledge it until the follow-up was attempted.
    await notifyTeam(lead, subject, false);
    if (!isNewsletter) {
      try {
        const sequence = await enrollLeadAutomation(lead, new URL(req.url).origin, { deferFirstReply: true });
        await sendInboundReply(sequence);
      } catch { /* The stored lead remains available in the CRM. */ }
      await forwardToGrowthOs(lead);
    }
    return json({ success: true, message: 'Received', submissionId, followUp: 'attempted' });
  }

  const work = processContactWork(submissionId).catch(error => {
    console.error('Contact follow-up remains queued:', submissionId, error);
  });
  if (typeof context?.waitUntil === 'function') context.waitUntil(work);
  else await work;

  return json({
    success: true,
    message: 'Received',
    submissionId,
    followUp: 'queued',
  });
}
