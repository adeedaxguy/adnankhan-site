import { getZohoStatus, listZohoInboxMessages, sendZohoEmail } from './zoho.js';
import { draftLeadReply, leadExpertise } from './lead-reply.js';
import { bookingNotifyEmails, busyCalendarIntervals, confirmBookingToLead, createCalendarEvent, notifyBooking } from './calendar.js';
import { createGoogleCalendarEvent, deleteGoogleCalendarEvent, getGoogleCalendarStatus, googleBusyIntervals } from './google-calendar.js';

const ADMIN_SECRET = process.env.ADMIN_SECRET;
const KV_URL = process.env.KV_REST_API_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN;

const CONFIG_KEY = 'agency:automation-config';
const SEQUENCE_KEY = 'agency:lead-sequences';
const OVERLAY_KEY = 'agency:lead-overlays';
const SUPPRESSION_KEY = 'agency:email-suppression';
const BOOKING_KEY = 'agency:bookings';
const SYNC_KEY = 'agency:automation-sync';
const DAY = 86400000;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const DEFAULT_CONFIG = {
  mode: 'review',
  initialDelayMinutes: 5,
  senderName: 'Adnan Khan',
  senderRole: 'Founder, Lofts Studio',
  phone: '+1 202 773 6947',
  whatsapp: '12027736947',
  complianceAddress: '',
  bookingNotificationEmails: '',
  trackOpens: false,
  trackClicks: false,
  booking: {
    enabled: true,
    timezone: 'Asia/Karachi',
    days: [1, 2, 3, 4, 5, 6],
    start: '17:00',
    end: '22:00',
    durationMinutes: 30,
    minimumNoticeHours: 12,
    horizonDays: 21,
  },
};

const STEP_DEFINITIONS = [
  { key: 'first-response', day: 0, label: 'Personal response' },
  { key: 'priority-fix', day: 1, label: 'Highest-impact fix' },
  { key: 'message-match', day: 3, label: 'Message-match framework' },
  { key: 'mini-audit', day: 7, label: 'Three-point mini audit' },
  { key: 'scope-choice', day: 14, label: 'Scope and timing' },
  { key: 'close-loop', day: 30, label: 'Close the loop' },
  { key: 'value-60', day: 60, label: 'Value follow-up', consentRequired: true },
  { key: 'value-90', day: 90, label: 'Final useful note', consentRequired: true },
];

function serviceError(code, message) {
  const error = new Error(message);
  error.code = code;
  return error;
}

export async function kvCmd(...args) {
  if (!KV_URL || !KV_TOKEN) throw serviceError('storage_unavailable', 'Agency storage is unavailable.');
  const response = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.error) throw serviceError('storage_unavailable', 'Agency storage is unavailable.');
  return payload.result ?? null;
}

function parseJson(value, fallback = null) {
  try { return typeof value === 'string' ? JSON.parse(value) : value; } catch { return fallback; }
}

function normalizeHash(result) {
  if (!result) return {};
  if (!Array.isArray(result)) return result;
  const output = {};
  for (let index = 0; index < result.length; index += 2) output[result[index]] = result[index + 1];
  return output;
}

function cleanProjectId(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 64);
}

function cleanEmail(value) {
  return String(value || '').trim().toLowerCase().slice(0, 254);
}

function cleanText(value, length = 500) {
  return String(value || '').replace(/\s+/g, ' ').trim().slice(0, length);
}

export function normalizeTimeZone(value, fallback = '') {
  const timezone = cleanText(value, 64);
  if (!timezone) return fallback;
  try {
    return new Intl.DateTimeFormat('en-US', { timeZone: timezone }).resolvedOptions().timeZone;
  } catch {
    return fallback;
  }
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[character]);
}

function htmlToText(value) {
  return String(value || '')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

function normalizeOrigin(value) {
  try {
    const url = new URL(value || 'https://lofts.studio');
    return `${url.protocol}//${url.host}`;
  } catch { return 'https://lofts.studio'; }
}

function safePublicUrl(value) {
  if (!value) return '';
  try {
    const candidate = /^https?:\/\//i.test(String(value)) ? String(value) : `https://${value}`;
    const url = new URL(candidate);
    if (!['http:', 'https:'].includes(url.protocol)) return '';
    const host = url.hostname.toLowerCase();
    if (host === 'localhost' || host.endsWith('.local') || host.endsWith('.internal')) return '';
    if (/^(127\.|10\.|0\.|169\.254\.|192\.168\.)/.test(host)) return '';
    const private172 = host.match(/^172\.(\d{1,3})\./);
    if (private172 && Number(private172[1]) >= 16 && Number(private172[1]) <= 31) return '';
    return url.href;
  } catch { return ''; }
}

function base64UrlEncode(value) {
  const bytes = typeof value === 'string' ? new TextEncoder().encode(value) : value;
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function base64UrlDecode(value) {
  const padded = String(value).replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(value.length / 4) * 4, '=');
  const binary = atob(padded);
  return Uint8Array.from(binary, character => character.charCodeAt(0));
}

async function signingKey() {
  if (!ADMIN_SECRET) throw serviceError('not_configured', 'Admin security is not configured.');
  return crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(`${ADMIN_SECRET}:ads-command-links-v1`),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign', 'verify'],
  );
}

export async function signAutomationToken(payload) {
  const encoded = base64UrlEncode(JSON.stringify({ v: 1, ...payload }));
  const signature = await crypto.subtle.sign('HMAC', await signingKey(), new TextEncoder().encode(encoded));
  return `${encoded}.${base64UrlEncode(new Uint8Array(signature))}`;
}

export async function verifyAutomationToken(token, expectedAction) {
  try {
    const [encoded, signature] = String(token || '').split('.');
    if (!encoded || !signature) return null;
    const valid = await crypto.subtle.verify(
      'HMAC',
      await signingKey(),
      base64UrlDecode(signature),
      new TextEncoder().encode(encoded),
    );
    if (!valid) return null;
    const payload = JSON.parse(new TextDecoder().decode(base64UrlDecode(encoded)));
    if (payload.v !== 1 || payload.a !== expectedAction || Number(payload.exp || 0) < Date.now()) return null;
    return payload;
  } catch { return null; }
}

function mergeConfig(value) {
  const booking = { ...DEFAULT_CONFIG.booking, ...(value?.booking || {}) };
  booking.days = Array.isArray(booking.days)
    ? booking.days.map(Number).filter(day => day >= 0 && day <= 6)
    : [...DEFAULT_CONFIG.booking.days];
  return {
    ...DEFAULT_CONFIG, ...(value || {}),
    initialDelayMinutes: Math.min(10, Math.max(1, Number(value?.initialDelayMinutes) || DEFAULT_CONFIG.initialDelayMinutes)),
    booking,
  };
}

export async function getAutomationConfig(projectId) {
  const id = cleanProjectId(projectId);
  const stored = parseJson(await kvCmd('HGET', CONFIG_KEY, id), null);
  const config = mergeConfig(stored);
  if (id === 'lofts-studio' && Number(stored?.booking?.availabilityVersion || 0) < 2) {
    config.booking = {
      ...config.booking, enabled: true, days: [0, 1, 2, 3, 4, 5, 6],
      start: '00:00', end: '24:00', minimumNoticeHours: 0, horizonDays: 21,
      availabilityVersion: 2,
    };
  }
  return config;
}

function sanitizeTime(value, fallback) {
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(String(value || '')) ? String(value) : fallback;
}

export async function automationReadiness(projectId, configInput) {
  const config = mergeConfig(configInput || await getAutomationConfig(projectId));
  const [zoho, googleCalendar] = await Promise.all([getZohoStatus(projectId), getGoogleCalendarStatus(projectId)]);
  const blockers = [];
  if (!zoho.connected) blockers.push('Connect Zoho Mail.');
  if (cleanProjectId(projectId) === 'lofts-studio' && zoho.connected && zoho.fromEmail !== 'hi@lofts.studio') blockers.push('Use hi@lofts.studio for customer-facing Zoho email and invitations.');
  if (zoho.needsReauthorization) blockers.push('Reauthorise Zoho for calendar access.');
  if (!googleCalendar.connected) blockers.push('Connect Google Calendar.');
  if (!cleanText(config.complianceAddress, 300)) blockers.push('Add a valid physical postal address for compliant follow-ups.');
  if (!config.booking.enabled) blockers.push('Enable booking before automated call invitations.');
  const bookingAlertRecipients = bookingNotifyEmails(config);
  if (bookingAlertRecipients.length < 2) blockers.push('Set both booking alert emails.');
  return { ready: blockers.length === 0, blockers, zoho, googleCalendar, bookingAlertRecipients };
}

export async function saveAutomationConfig(projectId, input) {
  const id = cleanProjectId(projectId);
  const previous = await getAutomationConfig(id);
  const mode = ['review', 'active', 'paused'].includes(input.mode) ? input.mode : previous.mode;
  const days = String(input.bookingDays || previous.booking.days.join(','))
    .split(',').map(Number).filter(day => Number.isInteger(day) && day >= 0 && day <= 6);
  const next = mergeConfig({
    ...previous,
    mode,
    initialDelayMinutes: Math.min(10, Math.max(1, Number(input.initialDelayMinutes) || previous.initialDelayMinutes)),
    senderName: cleanText(input.senderName ?? previous.senderName, 80),
    senderRole: cleanText(input.senderRole ?? previous.senderRole, 100),
    phone: cleanText(input.phone ?? previous.phone, 40),
    whatsapp: String(input.whatsapp ?? previous.whatsapp).replace(/\D/g, '').slice(0, 20),
    complianceAddress: cleanText(input.complianceAddress ?? previous.complianceAddress, 300),
    bookingNotificationEmails: String(input.bookingNotificationEmails ?? previous.bookingNotificationEmails)
      .split(/[;,]/).map(value => value.trim().toLowerCase()).filter(value => EMAIL_PATTERN.test(value)).slice(0, 5).join(', '),
    trackOpens: input.trackOpens === true,
    trackClicks: input.trackClicks === true,
    booking: {
      ...previous.booking,
      enabled: input.bookingEnabled !== false,
      timezone: cleanText(input.bookingTimezone ?? previous.booking.timezone, 64) || 'Asia/Karachi',
      days: days.length ? [...new Set(days)] : previous.booking.days,
      start: input.bookingAllDay === true ? '00:00' : sanitizeTime(input.bookingStart, previous.booking.start),
      end: input.bookingAllDay === true ? '24:00' : sanitizeTime(input.bookingEnd, previous.booking.end),
      durationMinutes: [15, 30, 45, 60].includes(Number(input.bookingDuration)) ? Number(input.bookingDuration) : previous.booking.durationMinutes,
      minimumNoticeHours: Math.min(168, Math.max(0, Number.isFinite(Number(input.minimumNoticeHours)) ? Number(input.minimumNoticeHours) : previous.booking.minimumNoticeHours)),
      horizonDays: Math.min(60, Math.max(7, Number(input.horizonDays) || previous.booking.horizonDays)),
    },
    updatedAt: Date.now(),
  });
  const readiness = await automationReadiness(id, next);
  if (next.mode === 'active' && !readiness.ready) {
    throw serviceError('not_ready', readiness.blockers.join(' '));
  }
  await kvCmd('HSET', CONFIG_KEY, id, JSON.stringify(next));
  return { config: next, readiness };
}

function extractMeta(html, name) {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const first = html.match(new RegExp(`<meta[^>]+name=["']${escaped}["'][^>]*content=["']([^"']*)["']`, 'i'));
  const second = html.match(new RegExp(`<meta[^>]+content=["']([^"']*)["'][^>]*name=["']${escaped}["']`, 'i'));
  return cleanText(first?.[1] || second?.[1], 300);
}

export async function analyzeLeadWebsite(lead) {
  const website = safePublicUrl(lead.website || lead.url || '');
  const fallback = {
    website,
    status: website ? 'unavailable' : 'not-provided',
    observations: website
      ? ['The website could not be checked automatically, so the first response should avoid unverified claims.']
      : ['No current website was provided; the first response should clarify the offer, audience, and traffic source.'],
    checkedAt: Date.now(),
  };
  if (!website) return fallback;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 3600);
  try {
    const response = await fetch(website, {
      signal: controller.signal,
      redirect: 'follow',
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; LoftsStudio-LeadReview/1.0)', Accept: 'text/html' },
    });
    const type = response.headers.get('content-type') || '';
    if (!response.ok || !type.includes('text/html')) return { ...fallback, httpStatus: response.status };
    const html = (await response.text()).slice(0, 500000);
    const title = cleanText(html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1], 180);
    const h1 = htmlToText(html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i)?.[1] || '').slice(0, 180);
    const description = extractMeta(html, 'description');
    const hasForm = /<form\b/i.test(html);
    const hasPrimaryCta = /\b(book|contact|get started|request|schedule|start|buy|shop|demo|quote|enquir)/i.test(htmlToText(html).slice(0, 14000));
    const hasProof = /\b(testimonial|case stud|reviews?|trusted by|clients?|results?)\b/i.test(htmlToText(html).slice(0, 30000));
    const observations = [];
    if (!h1) observations.push('The page does not expose a clear primary heading, so the offer may be harder to understand quickly.');
    else if (h1.length > 95) observations.push(`The main heading is long (${h1.length} characters); a tighter paid-traffic promise could improve message match.`);
    else observations.push(`The current main heading is “${h1}”; the ad landing page should mirror the exact search intent more directly.`);
    if (!hasForm) observations.push('No lead form was detected on the reviewed page, which adds an extra step before enquiry.');
    if (!hasPrimaryCta) observations.push('A strong primary action was not detected in the visible page copy.');
    if (!hasProof) observations.push('Proof such as reviews, outcomes, or client examples was not detected early in the page.');
    if (!description) observations.push('The page is missing a meta description, which weakens search presentation even though it does not directly control ad conversion.');
    if (observations.length < 2) observations.push('The strongest opportunity is a dedicated paid-traffic path with one promise, one action, and proof close to the decision point.');
    return {
      website: response.url || website,
      status: 'reviewed',
      httpStatus: response.status,
      title,
      heading: h1,
      description,
      hasForm,
      hasPrimaryCta,
      hasProof,
      observations: observations.slice(0, 4),
      checkedAt: Date.now(),
    };
  } catch {
    return fallback;
  } finally {
    clearTimeout(timer);
  }
}

function firstName(sequence) {
  return cleanText(sequence.lead?.name, 80).split(/\s+/)[0] || 'there';
}

function stepCopy(sequence, step) {
  const name = firstName(sequence);
  const lead = sequence.lead || {};
  const useCase = cleanText(lead.focus || lead.bottleneck || lead.scope, 140) || 'your project';
  const reviewed = sequence.analysis?.status === 'reviewed';
  const observation = reviewed ? sequence.analysis.observations?.[0] : '';
  const copies = {
    'first-response': null,
    'priority-fix': {
      subject: 'A useful first step for your project',
      body: `Hi ${name},\n\nI wanted to follow up on the priority you selected: ${useCase}. The first decision is usually what success should look like for the person using the site or product. That helps us choose the right scope and avoid work that will not move the result.\n\nIf you reply with the outcome that matters most, I can suggest a practical starting point. You can also choose a call time below.`,
    },
    'message-match': {
      subject: 'One question before we scope this',
      body: `Hi ${name},\n\nA useful question for the work you described (${useCase}): who needs to act differently once it is done? The answer tells us where to focus the design, development, or optimisation effort.\n\nIf you share the audience and the action you want them to take, I can make the next recommendation more specific.`,
    },
    'mini-audit': {
      subject: 'A short check for your project',
      body: `Hi ${name},\n\nI kept a note of your enquiry: ${useCase}.${observation ? ` One observation from the page you shared: ${observation}` : ' I would start by agreeing on the current obstacle, the desired result, and the first change worth testing.'}\n\nIf this is still a priority, reply with the part you would like me to look at first.`,
    },
    'scope-choice': {
      subject: 'Choosing the right scope',
      body: `Hi ${name},\n\nThe right scope for your enquiry (${useCase}) depends on what is already working and what has to change. A short call would let us separate a focused improvement from a larger rebuild and put the next step in writing.\n\nThe booking link is below if that would help.`,
    },
    'close-loop': {
      subject: 'Should I close the loop on this?',
      body: `Hi ${name},\n\nI have kept the notes from your Lofts Studio enquiry, but I do not want to keep following up if the timing is not right.\n\nShould I close this for now, or would a short call still be useful? Either answer is completely fine.`,
    },
    'value-60': {
      subject: 'A practical project checklist',
      body: `Hi ${name},\n\nA useful check for the work you described (${useCase}): can you name the intended user, the outcome they need, the current obstacle, and how you will know the change worked? Those four answers usually make the next decision much clearer.\n\nIf the project is active again, reply here or choose a time below.`,
    },
    'value-90': {
      subject: 'Closing the loop on your enquiry',
      body: `Hi ${name},\n\nI am closing my notes on your enquiry (${useCase}) for now so I do not keep filling your inbox. If the timing changes, reply to this email and we can pick up from there.`,
    },
  };
  return copies[step.key];
}

async function emailLinks(sequence, step, config) {
  const expires = Date.now() + 180 * DAY;
  const shared = { p: sequence.projectId, l: sequence.leadId, s: step.key, exp: expires };
  const bookingToken = await signAutomationToken({ ...shared, a: 'book' });
  const unsubscribeToken = await signAutomationToken({ ...shared, a: 'unsubscribe' });
  const openToken = await signAutomationToken({ ...shared, a: 'open' });
  const clickToken = await signAutomationToken({ ...shared, a: 'book-click' });
  const directBooking = `${sequence.origin}/book/?t=${encodeURIComponent(bookingToken)}`;
  return {
    booking: config.trackClicks
      ? `${sequence.origin}/api/email/click?t=${encodeURIComponent(clickToken)}`
      : directBooking,
    directBooking,
    unsubscribe: `${sequence.origin}/unsubscribe/?t=${encodeURIComponent(unsubscribeToken)}`,
    open: `${sequence.origin}/api/email/open?t=${encodeURIComponent(openToken)}`,
  };
}

function signatureHtml(config, links, includeUnsubscribe) {
  return `<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="border-top:1px solid #d7cec2;font-family:Arial,sans-serif;color:#171411">
    <tr><td style="padding-top:22px;line-height:1.55">
      <strong style="font-size:14px">${escapeHtml(config.senderName)}</strong><br>
      <span style="font-size:12px;color:#4f4942">${escapeHtml(config.senderRole)}</span><br>
      <a href="mailto:hi@lofts.studio" style="display:inline-block;margin-top:7px;color:#843322;font-size:12px;text-decoration:underline">hi@lofts.studio</a>
      ${config.complianceAddress ? `<div style="margin-top:12px;color:#4f4942;font-size:12px;line-height:1.5">${escapeHtml(config.complianceAddress)}</div>` : ''}
      ${includeUnsubscribe ? `<div style="margin-top:9px;font-size:12px"><a href="${escapeHtml(links.unsubscribe)}" style="color:#4f4942;text-decoration:underline">Stop follow-ups about this enquiry</a></div>` : ''}
    </td></tr>
  </table>`;
}

function plainSignature(config, links, includeUnsubscribe) {
  return [
    config.senderName,
    config.senderRole,
    `Book: ${links.directBooking}`,
    'hi@lofts.studio',
    'https://lofts.studio',
    config.complianceAddress || '',
    includeUnsubscribe ? `Stop follow-ups: ${links.unsubscribe}` : '',
  ].filter(Boolean).join('\n');
}

async function renderSequenceEmail(sequence, step, config, customCopy) {
  const copy = customCopy || stepCopy(sequence, step);
  const links = await emailLinks(sequence, step, config);
  const expertise = step.key === 'first-response' ? leadExpertise(sequence.lead) : null;
  const paragraphs = copy.body.split(/\n\n/).map(paragraph => {
    const lines = paragraph.split('\n').map(line => escapeHtml(line)).join('<br>');
    return `<p style="margin:0 0 19px;color:#171411;font-family:Arial,sans-serif;font-size:16px;line-height:1.65">${lines}</p>`;
  }).join('');
  const expertiseHtml = expertise ? `<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="border-top:1px solid #d7cec2;margin-top:9px">
    <tr><td style="padding:23px 0 7px;color:#171411;font-family:Georgia,serif;font-size:20px;line-height:1.3">Where we can help</td></tr>
    ${expertise.map(item => `<tr><td style="padding:5px 0;color:#4f4942;font-family:Arial,sans-serif;font-size:15px;line-height:1.55">${escapeHtml(item)}</td></tr>`).join('')}
  </table>` : '';
  const trackingAllowed = config.trackOpens && sequence.lead?.trackingConsent === 'yes';
  const html = `<!doctype html><html lang="en"><body style="margin:0;padding:0;background:#f4f0e9">
    <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background:#f4f0e9"><tr><td align="center" style="padding:24px 10px">
      <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;background:#fbfaf7;border-top:3px solid #a9432d">
        <tr><td style="padding:29px 30px 17px;color:#171411;font-family:'Iowan Old Style',Baskerville,'Palatino Linotype',Georgia,serif;font-size:27px;line-height:1.2">Lofts Studio<span style="color:#a9432d">.</span></td></tr>
        <tr><td style="padding:10px 30px 27px">
          ${paragraphs}
          ${expertiseHtml}
          <table role="presentation" cellpadding="0" cellspacing="0" style="margin:26px 0 27px"><tr><td bgcolor="#171411" style="background:#171411"><a href="${escapeHtml(links.booking)}" style="display:inline-block;padding:14px 21px;color:#fbfaf7;font-family:Arial,sans-serif;font-size:14px;font-weight:700;line-height:1.3;text-decoration:none">Choose a time to talk</a></td></tr></table>
          ${signatureHtml(config, links, true)}
        </td></tr>
        <tr><td style="padding:17px 30px;background:#ebe5db;color:#4f4942;font-family:Arial,sans-serif;font-size:12px;line-height:1.6">Lofts Studio &nbsp; | &nbsp; <a href="https://lofts.studio" style="color:#843322;text-decoration:underline">lofts.studio</a> &nbsp; | &nbsp; Reply to this email to continue the conversation.</td></tr>
      </table>
      ${trackingAllowed ? `<img src="${escapeHtml(links.open)}" width="1" height="1" alt="" style="display:block;border:0;width:1px;height:1px">` : ''}
    </td></tr></table></body></html>`;
  return {
    subject: copy.subject,
    text: [copy.body, expertise ? `Where we can help\n${expertise.join('\n')}` : '', plainSignature(config, links, true)].filter(Boolean).join('\n\n'),
    html,
    links,
  };
}

export async function buildCrmEmail(projectId, lead, subject, body, origin) {
  const config = await getAutomationConfig(projectId);
  const sequence = await getSequence(projectId, lead.id) || await enrollLeadAutomation({
    ...lead,
    _id: lead.id,
    _projectId: projectId,
    _ts: lead._ts || Date.now(),
  }, origin, { forceReview: true });
  if (!sequence) throw serviceError('sequence_unavailable', 'A booking link could not be created for this lead.');
  const step = { key: `manual-${Date.now()}`, label: 'Manual email' };
  return renderSequenceEmail(sequence, step, config, { subject: cleanText(subject, 180), body: String(body || '').trim().slice(0, 10000) });
}

async function saveSequence(sequence) {
  const field = `${sequence.projectId}:${sequence.leadId}`;
  await kvCmd('HSET', SEQUENCE_KEY, field, JSON.stringify({ ...sequence, updatedAt: Date.now() }));
}

export async function getSequence(projectId, leadId) {
  return parseJson(await kvCmd('HGET', SEQUENCE_KEY, `${cleanProjectId(projectId)}:${String(leadId).slice(0, 96)}`), null);
}

export async function listAutomationSequences(projectId) {
  const prefix = `${cleanProjectId(projectId)}:`;
  const stored = normalizeHash(await kvCmd('HGETALL', SEQUENCE_KEY));
  return Object.entries(stored)
    .filter(([field]) => field.startsWith(prefix))
    .map(([, value]) => parseJson(value, null))
    .filter(Boolean)
    .sort((a, b) => Number(b.createdAt || 0) - Number(a.createdAt || 0));
}

async function appendLeadActivity(projectId, leadId, event, patch = {}) {
  const key = `${cleanProjectId(projectId)}:${String(leadId).slice(0, 96)}`;
  const current = parseJson(await kvCmd('HGET', OVERLAY_KEY, key), {}) || {};
  const fingerprint = cleanText(event.eventId || `${event.type}:${event.at}:${event.messageId || ''}`, 200);
  if ((current.activity || []).some(item => item.eventId === fingerprint)) return current;
  const next = {
    ...current,
    ...patch,
    activity: [{ ...event, eventId: fingerprint }, ...(current.activity || [])].slice(0, 80),
    updatedAt: event.at || Date.now(),
  };
  await kvCmd('HSET', OVERLAY_KEY, key, JSON.stringify(next));
  return next;
}

function nextPendingIndex(sequence, from = 0) {
  const steps = sequence.steps || [];
  for (let index = Math.max(0, from); index < steps.length; index += 1) {
    if (steps[index].status === 'pending') return index;
  }
  return steps.length;
}

async function sendStep(sequence, stepIndex, options = {}) {
  const config = await getAutomationConfig(sequence.projectId);
  const readiness = await automationReadiness(sequence.projectId, config);
  const step = sequence.steps?.[stepIndex];
  const firstResponsePreview = options.force && step?.key === 'first-response';
  if (!options.force && config.mode !== 'active') throw serviceError('automation_paused', 'Automation is not active.');
  const blockers = firstResponsePreview
    ? readiness.blockers.filter(blocker => blocker !== 'Add a valid physical postal address for compliant follow-ups.')
    : readiness.blockers;
  if (blockers.length) throw serviceError('not_ready', blockers.join(' '));
  if (!step || step.status !== 'pending') return sequence;
  if (step.consentRequired && sequence.lead?.nurtureConsent !== 'yes') {
    step.status = 'skipped';
    step.skipReason = 'Extended nurture consent not recorded';
    sequence.nextStepIndex = nextPendingIndex(sequence, stepIndex + 1);
    sequence.status = sequence.nextStepIndex >= sequence.steps.length ? 'completed' : sequence.status;
    await saveSequence(sequence);
    return sequence;
  }
  step.status = 'sending';
  step.sendingAt = Date.now();
  await saveSequence(sequence);
  let mailAccepted = false;
  try {
    const customCopy = step.key === 'first-response' ? await draftLeadReply(sequence.lead, sequence.analysis) : null;
    const rendered = await renderSequenceEmail(sequence, step, config, customCopy);
    const scheduleAt = options.scheduleAt || null;
    const sent = await sendZohoEmail(sequence.projectId, {
      toAddress: sequence.lead.email,
      subject: rendered.subject,
      content: rendered.text,
      htmlContent: rendered.html,
      scheduleAt,
    });
    mailAccepted = true;
    step.status = scheduleAt ? 'scheduled' : 'sent';
    step.subject = rendered.subject;
    step.sentAt = sent.sentAt;
    step.scheduledFor = sent.scheduledFor;
    step.messageId = sent.messageId;
    sequence.status = firstResponsePreview && sequence.status !== 'active' ? 'review' : 'active';
    sequence.lastError = null;
    sequence.lastSentAt = scheduleAt || sent.sentAt;
    sequence.nextStepIndex = nextPendingIndex(sequence, stepIndex + 1);
    if (sequence.nextStepIndex >= sequence.steps.length) sequence.status = 'completed';
    await saveSequence(sequence);
    await appendLeadActivity(sequence.projectId, sequence.leadId, {
      type: 'email',
      direction: 'outbound',
      provider: 'zoho',
      status: scheduleAt ? 'scheduled' : 'sent',
      to: sequence.lead.email,
      subject: rendered.subject,
      body: rendered.text.slice(0, 4000),
      messageId: sent.messageId,
      at: sent.sentAt,
      scheduledFor: sent.scheduledFor,
      eventId: `email:${sequence.leadId}:${step.key}`,
    }, { stage: 'contacted' });
    return sequence;
  } catch (error) {
    step.status = mailAccepted ? 'needs-review' : 'pending';
    step.error = cleanText(error.message, 300);
    sequence.status = mailAccepted ? 'needs-review' : 'blocked';
    sequence.lastError = step.error;
    try { await saveSequence(sequence); } catch { /* Preserve the original delivery ambiguity. */ }
    throw error;
  }
}

function isTestLead(lead) {
  return /(\btest(?:ing|er)?\b|\bqa\b|codex|example\.com|\.test\b)/i.test([lead.name, lead.email].filter(Boolean).join(' '))
    || /\b(do not contact|debug submission)\b/i.test(String(lead.message || ''));
}

export async function enrollLeadAutomation(lead, origin = 'https://lofts.studio', options = {}) {
  const projectId = cleanProjectId(lead._projectId || lead.projectId || 'lofts-studio');
  const leadId = String(lead._id || lead.id || '').slice(0, 96);
  const email = cleanEmail(lead.email);
  if (!projectId || !leadId || !email || lead.source === 'footer-newsletter') return null;
  const existing = await getSequence(projectId, leadId);
  if (existing) return existing;
  const suppressed = await kvCmd('HGET', SUPPRESSION_KEY, email);
  const config = await getAutomationConfig(projectId);
  const testLead = isTestLead(lead);
  const createdAt = Number(lead._ts) || Date.now();
  const analysis = await analyzeLeadWebsite(lead);
  const sequence = {
    id: crypto.randomUUID(),
    projectId,
    leadId,
    origin: normalizeOrigin(origin),
    status: suppressed ? 'suppressed' : options.forceReview || testLead ? 'review' : config.mode === 'active' ? 'active' : config.mode === 'paused' ? 'paused' : 'review',
    modeAtEnrollment: config.mode,
    createdAt,
    updatedAt: createdAt,
    nextStepIndex: 0,
    lead: {
      name: cleanText(lead.name, 120),
      email,
      phone: cleanText(lead.phone, 60),
      website: analysis.website || safePublicUrl(lead.website || lead.url),
      bottleneck: cleanText(lead.bottleneck || lead.scope, 300),
      focus: cleanText(lead.focus, 300),
      message: cleanText(lead.message, 1000),
      pageTitle: cleanText(lead.page_title, 180),
      sourcePath: cleanText(lead.source_path, 200),
      country: cleanText(lead.country, 80),
      timezone: normalizeTimeZone(lead.timezone),
      source: cleanText(lead.source, 100),
      nurtureConsent: String(lead.nurtureConsent || '').toLowerCase() === 'yes' ? 'yes' : 'no',
      trackingConsent: String(lead.trackingConsent || '').toLowerCase() === 'yes' ? 'yes' : 'no',
      consentNotice: cleanText(lead.consentNotice, 500),
    },
    analysis,
    steps: STEP_DEFINITIONS.map(definition => ({
      ...definition,
      dueAt: definition.day === 0
        ? createdAt + config.initialDelayMinutes * 60000
        : createdAt + definition.day * DAY,
      status: 'pending',
    })),
  };
  await saveSequence(sequence);
  await appendLeadActivity(projectId, leadId, {
    type: 'automation',
    status: sequence.status,
    at: Date.now(),
    eventId: `automation:enrolled:${leadId}`,
  });
  if (sequence.status === 'active' && !options.deferFirstReply) {
    try {
      return await sendStep(sequence, 0, { scheduleAt: sequence.steps[0].dueAt });
    } catch {
      return sequence;
    }
  }
  return sequence;
}

export async function sendInboundReply(sequence) {
  if (!sequence || ['suppressed', 'unsubscribed', 'paused'].includes(sequence.status)) return { status: 'skipped' };
  const step = sequence.steps?.[0];
  if (!step || step.status !== 'pending') return { status: 'already-handled' };
  if (isTestLead(sequence.lead)) return { status: 'review' };
  step.status = 'sending';
  step.sendingAt = Date.now();
  await saveSequence(sequence);
  let accepted = false;
  try {
    const config = await getAutomationConfig(sequence.projectId);
    const copy = await draftLeadReply(sequence.lead, sequence.analysis);
    const rendered = await renderSequenceEmail(sequence, step, config, copy);
    const scheduledFor = Math.max(Date.now() + 60000, Number(step.dueAt) || 0);
    let sent;
    let deliveryStatus = 'scheduled';
    try {
      sent = await sendZohoEmail(sequence.projectId, {
        toAddress: sequence.lead.email,
        subject: rendered.subject,
        htmlContent: rendered.html,
        scheduleAt: scheduledFor,
      });
    } catch (error) {
      if (error?.code !== 'send_failed' || !/PATTERN_NOT_MATCHED/.test(error.message || '')) throw error;
      sent = await sendZohoEmail(sequence.projectId, {
        toAddress: sequence.lead.email,
        subject: rendered.subject,
        htmlContent: rendered.html,
      });
      deliveryStatus = 'sent';
    }
    accepted = true;
    step.status = deliveryStatus;
    step.subject = rendered.subject;
    step.sentAt = sent.sentAt;
    step.scheduledFor = deliveryStatus === 'scheduled' ? scheduledFor : null;
    step.messageId = sent.messageId;
    sequence.nextStepIndex = nextPendingIndex(sequence, 1);
    sequence.lastSentAt = step.scheduledFor || sent.sentAt;
    sequence.lastError = null;
    await saveSequence(sequence);
    await appendLeadActivity(sequence.projectId, sequence.leadId, {
      type: 'email', direction: 'outbound', provider: 'zoho', status: deliveryStatus,
      to: sequence.lead.email, subject: rendered.subject, body: rendered.text.slice(0, 4000),
      messageId: sent.messageId, at: sent.sentAt, scheduledFor: step.scheduledFor,
      eventId: `email:${sequence.leadId}:first-response`,
    }, { stage: 'contacted' });
    return { status: deliveryStatus };
  } catch (error) {
    step.status = accepted ? 'needs-review' : 'pending';
    sequence.status = 'needs-review';
    sequence.lastError = accepted
      ? 'Delivery was accepted but the CRM update needs review.'
      : cleanText(error?.message, 300) || 'The automatic first reply could not be sent.';
    try { await saveSequence(sequence); } catch { /* Keep the original delivery state for review. */ }
    return { status: 'delayed' };
  }
}

function extractAddress(value) {
  const decoded = String(value || '').replace(/&quot;|&#34;/gi, '"').replace(/&lt;/gi, '<').replace(/&gt;/gi, '>');
  const bracket = decoded.match(/<([^<>\s]+@[^<>\s]+)>/);
  const plain = decoded.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
  return cleanEmail(bracket?.[1] || plain?.[0] || decoded);
}

function messageTime(message) {
  const value = Number(message.receivedTime || message.sentDateInGMT || message.receivedTimeInGMT || 0);
  return value > 0 && value < 1000000000000 ? value * 1000 : value;
}

function isAutomatedMailboxMessage(message) {
  const subject = cleanText(message.subject, 220);
  const sender = cleanText(message.fromAddress || message.sender, 220);
  return /(automatic reply|auto.?reply|out of office|away from the office|delivery status|undeliverable|mail delivery subsystem)/i.test(`${subject} ${sender}`);
}

export async function syncZohoReplies(projectId) {
  const id = cleanProjectId(projectId);
  const sequences = await listAutomationSequences(id);
  const messages = await listZohoInboxMessages(id, 200);
  const byEmail = new Map();
  for (const message of messages) {
    const address = extractAddress(message.fromAddress || message.sender);
    if (!address) continue;
    const list = byEmail.get(address) || [];
    list.push(message);
    byEmail.set(address, list);
  }
  let replies = 0;
  for (const sequence of sequences) {
    if (['replied', 'booked', 'unsubscribed', 'stopped', 'completed', 'suppressed'].includes(sequence.status)) continue;
    const message = (byEmail.get(cleanEmail(sequence.lead?.email)) || [])
      .filter(item => !isAutomatedMailboxMessage(item))
      .filter(item => messageTime(item) >= Number(sequence.createdAt || 0) - 3600000)
      .sort((a, b) => messageTime(b) - messageTime(a))[0];
    if (!message) continue;
    const messageId = String(message.messageId || '');
    if (messageId && sequence.lastReplyMessageId === messageId) continue;
    sequence.status = 'replied';
    sequence.repliedAt = messageTime(message) || Date.now();
    sequence.lastReplyMessageId = messageId;
    sequence.replySubject = cleanText(message.subject, 180);
    sequence.replySummary = htmlToText(message.summary || '').slice(0, 500);
    await saveSequence(sequence);
    await appendLeadActivity(id, sequence.leadId, {
      type: 'reply',
      direction: 'inbound',
      subject: sequence.replySubject,
      summary: sequence.replySummary,
      messageId,
      at: sequence.repliedAt,
      eventId: `reply:${messageId || sequence.repliedAt}`,
    });
    replies += 1;
  }
  await kvCmd('HSET', SYNC_KEY, id, JSON.stringify({ lastReplySyncAt: Date.now(), messagesChecked: messages.length, replies }));
  return { lastReplySyncAt: Date.now(), messagesChecked: messages.length, replies };
}

export async function processDueAutomations(projectId) {
  const configuredIds = projectId ? [] : await kvCmd('HKEYS', CONFIG_KEY);
  const ids = projectId
    ? [cleanProjectId(projectId)]
    : [...new Set(['lofts-studio', ...(Array.isArray(configuredIds) ? configuredIds : [])])].filter(Boolean);
  const result = { projects: [], sent: 0, skipped: 0, errors: [] };
  for (const id of ids) {
    const config = await getAutomationConfig(id);
    if (config.mode !== 'active') {
      result.projects.push({ projectId: id, status: config.mode });
      continue;
    }
    try {
      await syncZohoReplies(id);
    } catch (error) {
      result.errors.push({ projectId: id, error: cleanText(error.message, 300) });
      continue;
    }
    const sequences = await listAutomationSequences(id);
    for (const sequence of sequences.slice(0, 500)) {
      if (!['active', 'blocked'].includes(sequence.status)) continue;
      if ((sequence.steps || []).some(step => step.status === 'sending')) {
        sequence.status = 'needs-review';
        sequence.lastError = 'A previous delivery attempt did not reach a final saved state. Review it manually before sending again.';
        await saveSequence(sequence);
        result.errors.push({ projectId: id, leadId: sequence.leadId, error: sequence.lastError });
        continue;
      }
      const index = nextPendingIndex(sequence, sequence.nextStepIndex || 0);
      const step = sequence.steps?.[index];
      if (!step || Number(step.dueAt || 0) > Date.now()) continue;
      const lockKey = `agency:automation-lock:${id}:${sequence.leadId}:${step.key}`;
      const locked = await kvCmd('SET', lockKey, String(Date.now()), 'NX', 'EX', '900');
      if (!locked) continue;
      try {
        const before = step.status;
        const updated = await sendStep(sequence, index);
        if (updated.steps[index]?.status === 'skipped') result.skipped += 1;
        else if (before !== updated.steps[index]?.status) result.sent += 1;
      } catch (error) {
        result.errors.push({ projectId: id, leadId: sequence.leadId, error: cleanText(error.message, 300) });
      }
    }
    result.projects.push({ projectId: id, status: 'processed' });
  }
  return result;
}

export async function controlSequence(projectId, leadId, action) {
  const sequence = await getSequence(projectId, leadId);
  if (!sequence) throw serviceError('not_found', 'No automation sequence exists for this lead.');
  if (action === 'pause') sequence.status = 'paused';
  else if (action === 'stop') sequence.status = 'stopped';
  else if (action === 'resume') {
    const readiness = await automationReadiness(projectId);
    if (!readiness.ready) throw serviceError('not_ready', readiness.blockers.join(' '));
    sequence.status = 'active';
  } else if (action === 'send-next') {
    await syncZohoReplies(projectId);
    const fresh = await getSequence(projectId, leadId);
    if (fresh.status === 'replied') throw serviceError('already_replied', 'This lead has replied. The sequence was stopped.');
    return sendStep(fresh, nextPendingIndex(fresh, fresh.nextStepIndex || 0), { force: true });
  } else throw serviceError('invalid_action', 'Unknown sequence action.');
  await saveSequence(sequence);
  await appendLeadActivity(projectId, leadId, {
    type: 'automation', status: sequence.status, at: Date.now(), eventId: `automation:${action}:${Date.now()}`,
  });
  return sequence;
}

export async function stopSequenceForStage(projectId, leadId, stage) {
  if (!['qualified', 'proposal', 'won', 'lost'].includes(stage)) return;
  const sequence = await getSequence(projectId, leadId);
  if (!sequence || ['replied', 'booked', 'unsubscribed', 'stopped', 'completed'].includes(sequence.status)) return;
  sequence.status = 'stopped';
  sequence.stopReason = `CRM stage changed to ${stage}`;
  await saveSequence(sequence);
}

export async function recordEmailEngagement(token, action, meta = {}) {
  const payload = await verifyAutomationToken(token, action);
  if (!payload) throw serviceError('invalid_token', 'This tracking link is invalid or expired.');
  const sequence = await getSequence(payload.p, payload.l);
  if (!sequence) throw serviceError('not_found', 'The lead sequence no longer exists.');
  const eventId = `${action}:${payload.p}:${payload.l}:${payload.s}`;
  const first = await kvCmd('SADD', 'agency:engagement-dedupe', eventId);
  if (Number(first) === 1) {
    const type = action === 'open' ? 'open' : 'click';
    await appendLeadActivity(payload.p, payload.l, {
      type,
      step: payload.s,
      confidence: action === 'open' ? 'estimated' : 'likely',
      userAgent: cleanText(meta.userAgent, 220),
      at: Date.now(),
      eventId,
    });
  }
  return { payload, sequence };
}

export async function unsubscribeLead(token) {
  const payload = await verifyAutomationToken(token, 'unsubscribe');
  if (!payload) throw serviceError('invalid_token', 'This unsubscribe link is invalid or expired.');
  const sequence = await getSequence(payload.p, payload.l);
  if (!sequence) throw serviceError('not_found', 'The enquiry could not be found.');
  sequence.status = 'unsubscribed';
  sequence.unsubscribedAt = Date.now();
  await saveSequence(sequence);
  await kvCmd('HSET', SUPPRESSION_KEY, cleanEmail(sequence.lead.email), JSON.stringify({
    projectId: payload.p,
    leadId: payload.l,
    reason: 'unsubscribe',
    at: sequence.unsubscribedAt,
  }));
  await appendLeadActivity(payload.p, payload.l, {
    type: 'unsubscribe', at: sequence.unsubscribedAt, eventId: `unsubscribe:${payload.p}:${payload.l}`,
  });
  return { email: sequence.lead.email, at: sequence.unsubscribedAt };
}

function zonedParts(date, timeZone) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23',
  }).formatToParts(date);
  return Object.fromEntries(parts.filter(part => part.type !== 'literal').map(part => [part.type, Number(part.value)]));
}

function zonedDateToUtc(year, month, day, hour, minute, timeZone) {
  const target = Date.UTC(year, month - 1, day, hour, minute, 0);
  let guess = target;
  for (let pass = 0; pass < 2; pass += 1) {
    const parts = zonedParts(new Date(guess), timeZone);
    const represented = Date.UTC(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, parts.second);
    guess -= represented - target;
  }
  return new Date(guess);
}

function localDateSequence(timeZone, horizonDays) {
  const today = zonedParts(new Date(), timeZone);
  const dates = [];
  for (let offset = 0; offset < horizonDays; offset += 1) {
    const date = new Date(Date.UTC(today.year, today.month - 1, today.day + offset, 12));
    dates.push({
      year: date.getUTCFullYear(),
      month: date.getUTCMonth() + 1,
      day: date.getUTCDate(),
      weekday: date.getUTCDay(),
    });
  }
  return dates;
}

function minutesFromTime(value) {
  const [hour, minute] = String(value).split(':').map(Number);
  return hour * 60 + minute;
}

export async function getBookingContext(token) {
  const payload = await verifyAutomationToken(token, 'book');
  if (!payload) throw serviceError('invalid_token', 'This booking link is invalid or expired.');
  const sequence = await getSequence(payload.p, payload.l);
  if (!sequence || ['unsubscribed', 'suppressed'].includes(sequence.status)) throw serviceError('not_found', 'This booking link is no longer available.');
  return { payload, sequence, config: await getAutomationConfig(payload.p) };
}

export async function getAvailableSlots(token) {
  const { payload, sequence, config } = await getBookingContext(token);
  if (sequence.bookingId) {
    const existing = parseJson(await kvCmd('HGET', BOOKING_KEY, sequence.bookingId));
    if (existing) return { booking: existing };
  }
  if (!config.booking.enabled) throw serviceError('booking_disabled', 'Online booking is not currently available.');
  const zohoStatus = await getZohoStatus(payload.p);
  if (!bookingNotifyEmails(config).length || !zohoStatus.connected || (payload.p === 'lofts-studio' && zohoStatus.fromEmail !== 'hi@lofts.studio')) {
    throw serviceError('booking_unavailable', 'Online booking is unavailable right now. Please email hi@lofts.studio.');
  }
  const booking = config.booking;
  const startMinutes = minutesFromTime(booking.start);
  const endMinutes = minutesFromTime(booking.end);
  const earliest = Date.now() + booking.minimumNoticeHours * 3600000;
  const candidates = [];
  const seenStarts = new Set();
  for (const date of localDateSequence(booking.timezone, booking.horizonDays)) {
    if (!booking.days.includes(date.weekday)) continue;
    for (let minute = startMinutes; minute + booking.durationMinutes <= endMinutes; minute += booking.durationMinutes) {
      const start = zonedDateToUtc(date.year, date.month, date.day, Math.floor(minute / 60), minute % 60, booking.timezone);
      if (start.getTime() < earliest) continue;
      const local = zonedParts(start, booking.timezone);
      if (local.year !== date.year || local.month !== date.month || local.day !== date.day
        || local.hour !== Math.floor(minute / 60) || local.minute !== minute % 60) continue;
      const iso = start.toISOString();
      if (!seenStarts.has(iso)) {
        seenStarts.add(iso);
        candidates.push(iso);
      }
    }
  }
  const lockKeys = candidates.map(start => `agency:booking-lock:${start}`);
  const locks = lockKeys.length ? await kvCmd('MGET', ...lockKeys) : [];
  const rangeStart = candidates[0] || new Date().toISOString();
  const rangeEnd = new Date(new Date(candidates[candidates.length - 1] || rangeStart).getTime() + booking.durationMinutes * 60000);
  const [zohoResult, googleResult] = await Promise.allSettled([
    busyCalendarIntervals(payload.p, rangeStart, rangeEnd),
    googleBusyIntervals(payload.p, rangeStart, rangeEnd),
  ]);
  if (zohoResult.status === 'rejected') console.warn('Zoho booking availability unavailable:', zohoResult.reason?.message);
  if (googleResult.status === 'rejected') console.warn('Google booking availability unavailable:', googleResult.reason?.message);
  const zohoBusy = zohoResult.status === 'fulfilled' ? zohoResult.value : null;
  const googleBusy = googleResult.status === 'fulfilled' ? googleResult.value : null;
  const busy = [...(zohoBusy || []), ...(googleBusy || [])];
  const slots = candidates.filter((start, index) => {
    if (Array.isArray(locks) && locks[index]) return false;
    const at = new Date(start).getTime();
    return !busy.some(interval => at < interval.end && at + booking.durationMinutes * 60000 > interval.start);
  });
  return {
    projectId: payload.p,
    lead: { name: sequence.lead.name, email: sequence.lead.email, phone: sequence.lead.phone, timezone: sequence.lead.timezone || '' },
    timezone: booking.timezone,
    durationMinutes: booking.durationMinutes,
    calendarConnected: zohoBusy !== null && googleBusy !== null
      && (payload.p !== 'lofts-studio' || zohoStatus.fromEmail === 'hi@lofts.studio'),
    googleCalendarConnected: googleBusy !== null,
    slots,
  };
}

export async function createBooking(token, input) {
  const context = await getBookingContext(token);
  if (context.sequence.bookingId) {
    const existing = parseJson(await kvCmd('HGET', BOOKING_KEY, context.sequence.bookingId));
    if (existing) return { booking: existing, warning: '' };
  }
  const availability = await getAvailableSlots(token);
  if (availability.booking) return { booking: availability.booking, warning: '' };
  const start = String(input.start || '');
  if (!availability.slots.includes(start)) throw serviceError('slot_unavailable', 'That time is no longer available. Choose another slot.');
  const phone = cleanText(input.phone || context.sequence.lead.phone, 60);
  if (phone.replace(/\D/g, '').length < 7 || phone.replace(/\D/g, '').length > 15 || !/^[+\d\s().-]+$/.test(phone)) {
    throw serviceError('invalid_phone', 'Enter a valid phone or WhatsApp number, including your country code.');
  }
  const lockKey = `agency:booking-lock:${start}`;
  const bookingId = crypto.randomUUID();
  const locked = await kvCmd('SET', lockKey, bookingId, 'NX', 'EX', String(120 * 86400));
  if (!locked) throw serviceError('slot_unavailable', 'That time was just booked. Choose another slot.');
  const startAt = new Date(start).getTime();
  const booking = {
    id: bookingId,
    projectId: context.payload.p,
    leadId: context.payload.l,
    leadName: cleanText(input.name || context.sequence.lead.name, 120),
    leadEmail: context.sequence.lead.email,
    focus: cleanText(context.sequence.lead.focus || context.sequence.lead.bottleneck || context.sequence.lead.message, 240),
    phone,
    note: cleanText(input.note, 1000),
    startAt,
    endAt: startAt + availability.durationMinutes * 60000,
    bookingTimezone: normalizeTimeZone(input.timezone, context.sequence.lead.timezone || availability.timezone),
    hostTimezone: availability.timezone,
    durationMinutes: availability.durationMinutes,
    createdAt: Date.now(),
    status: availability.calendarConnected ? 'confirmed' : 'requested',
  };
  if (availability.calendarConnected) {
    let googleEvent = null;
    try {
      googleEvent = await createGoogleCalendarEvent(booking);
      const calendarEvent = await createCalendarEvent(booking);
      if (calendarEvent.status !== 'created') throw new Error('Calendar event could not be created.');
      booking.calendarStatus = calendarEvent.status;
      booking.calendarEventUid = calendarEvent.uid;
      booking.calendarUid = calendarEvent.calendarUid;
      booking.googleEventId = googleEvent.id;
    } catch (error) {
      if (googleEvent) {
        let rolledBack = false;
        try {
          await deleteGoogleCalendarEvent(context.payload.p, googleEvent.id);
          rolledBack = true;
        } catch {
          booking.googleEventId = googleEvent.id;
        }
        booking.status = 'requested';
        booking.calendarStatus = rolledBack ? 'zoho-review' : 'partial-google';
      }
      if (!googleEvent) {
        await kvCmd('DEL', lockKey);
        throw error;
      }
    }
  } else if (availability.googleCalendarConnected) {
    try {
      const googleEvent = await createGoogleCalendarEvent(booking);
      booking.googleEventId = googleEvent.id;
      booking.calendarStatus = 'partial-google';
    } catch {
      booking.calendarStatus = 'not-connected';
    }
  } else {
    booking.calendarStatus = 'not-connected';
  }
  await kvCmd('HSET', BOOKING_KEY, bookingId, JSON.stringify(booking));
  context.sequence.status = 'booked';
  context.sequence.bookedAt = booking.createdAt;
  context.sequence.bookingId = bookingId;
  await saveSequence(context.sequence);
  await appendLeadActivity(context.payload.p, context.payload.l, {
    type: 'booking',
    bookingId,
    status: booking.status,
    startAt,
    durationMinutes: booking.durationMinutes,
    at: booking.createdAt,
    eventId: `booking:${bookingId}`,
  }, {
    stage: booking.status === 'confirmed' ? 'qualified' : 'contacted',
    nextAction: `${booking.status === 'confirmed' ? 'Call booked' : 'Confirm requested call'} for ${new Date(startAt).toISOString()}`,
  });
  let warning = '';
  try {
    if (!await notifyBooking(booking, context.config)) warning = 'The booking was saved, but the team notification needs review.';
  } catch {
    warning = 'The booking was saved, but the team notification needs review.';
  }
  try {
    if (!await confirmBookingToLead(booking, context.config)) warning = 'The booking was saved, but the confirmation email needs review.';
  } catch (error) {
    warning = `The booking is saved, but the confirmation email could not be sent: ${cleanText(error.message, 180)}`;
  }
  return { booking, warning };
}

export async function getAutomationSnapshot(projectId) {
  const id = cleanProjectId(projectId);
  const [config, readiness, sequences, sync] = await Promise.all([
    getAutomationConfig(id),
    automationReadiness(id),
    listAutomationSequences(id),
    kvCmd('HGET', SYNC_KEY, id).then(value => parseJson(value, null)),
  ]);
  return {
    config,
    readiness,
    sync,
    sequences,
    summary: {
      total: sequences.length,
      active: sequences.filter(item => item.status === 'active').length,
      review: sequences.filter(item => item.status === 'review').length,
      replied: sequences.filter(item => item.status === 'replied').length,
      booked: sequences.filter(item => item.status === 'booked').length,
      stopped: sequences.filter(item => ['stopped', 'unsubscribed', 'suppressed'].includes(item.status)).length,
    },
  };
}
