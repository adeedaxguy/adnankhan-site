import { getZohoStatus, listZohoInboxMessages, sendZohoEmail } from '../_lib/zoho.js';
import { kvCmd } from '../_lib/automation.js';

export const config = { runtime: 'edge' };

const PROJECT_ID = 'lofts-studio';
export const DAILY_NEW_LIMIT = 100;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function json(status, payload) {
  return new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store, private', 'X-Content-Type-Options': 'nosniff' } });
}

async function digest(value) {
  return new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value)));
}

async function authorized(req) {
  const expected = String(process.env.GROWTH_OS_SERVICE_TOKEN || '').trim();
  const supplied = String(req.headers.get('authorization') || '').replace(/^Bearer\s+/i, '').trim();
  if (expected.length < 32 || !supplied) return false;
  const [left, right] = await Promise.all([digest(expected), digest(supplied)]);
  let difference = 0;
  for (let index = 0; index < left.length; index += 1) difference |= left[index] ^ right[index];
  return difference === 0;
}

function cleanEmail(value) {
  return String(value || '').trim().toLowerCase().slice(0, 254);
}

function cleanText(value, limit) {
  return String(value || '').trim().slice(0, limit);
}

export function zohoMessage(toAddress, subject, content, mailFormat, replyToMessageId) {
  const message = mailFormat === 'html'
    ? { toAddress, subject, htmlContent: content }
    : { toAddress, subject, content };
  if (replyToMessageId) message.replyToMessageId = cleanText(replyToMessageId, 200);
  return message;
}

function messageTime(message) {
  const raw = Number(message.receivedTime || message.sentDateInGMT || message.receivedTimeInGMT || 0);
  return raw > 0 && raw < 1000000000000 ? raw * 1000 : raw;
}

export default async function handler(req) {
  if (!(await authorized(req))) return json(401, { error: 'Unauthorized.' });
  if (req.method === 'GET') {
    try {
      const status = await getZohoStatus(PROJECT_ID);
      return json(200, {
        ok: status.connected && !status.needsReauthorization,
        provider: status.provider,
        sender: status.fromEmail,
        permission: status.permission,
        needsReauthorization: status.needsReauthorization,
        checkedAt: new Date().toISOString(),
      });
    } catch {
      return json(503, { error: 'Lofts Mail connection is unavailable.' });
    }
  }
  if (req.method !== 'POST') return json(405, { error: 'Method not allowed.' });

  const body = await req.json().catch(() => null);
  if (!body || typeof body !== 'object') return json(400, { error: 'Invalid JSON body.' });
  if (body.action === 'sync') return syncReplies(body);
  if (body.action !== 'send') return json(400, { error: 'Unsupported action.' });
  return sendMessage(req, body);
}

async function syncReplies(body) {
  try {
    const after = Math.max(0, Number(body.after || 0));
    const rows = await listZohoInboxMessages(PROJECT_ID, Math.min(200, Math.max(1, Number(body.limit || 100))));
    const replies = rows
      .map(message => ({
        id: String(message.messageId || message.messageID || ''),
        inReplyTo: String(message.inReplyTo || message.inReplyToMessageId || '') || null,
        fromAddress: cleanEmail(message.fromAddress || message.sender),
        subject: cleanText(message.subject, 300),
        text: cleanText(message.summary || message.subject || 'Inbound reply received.', 2000),
        receivedAt: messageTime(message),
      }))
      .filter(message => message.id && message.receivedAt > after)
      .sort((a, b) => a.receivedAt - b.receivedAt);
    return json(200, { replies, nextCursor: replies.at(-1)?.receivedAt ? String(replies.at(-1).receivedAt) : String(after) });
  } catch {
    return json(502, { error: 'Lofts Mail reply sync failed.' });
  }
}

async function sendMessage(req, body) {
  const idempotencyKey = cleanText(req.headers.get('idempotency-key'), 160);
  const toAddress = cleanEmail(body.toAddress);
  const subject = cleanText(body.subject, 180);
  const mailFormat = body.mailFormat === 'html' ? 'html' : 'plaintext';
  const content = cleanText(body.content, mailFormat === 'html' ? 30000 : 10000);
  const kind = ['new', 'reply', 'transactional'].includes(body.kind) ? body.kind : 'new';
  if (idempotencyKey.length < 16 || !EMAIL_PATTERN.test(toAddress) || !subject || !content) {
    return json(400, { error: 'A valid recipient, message, and idempotency key are required.' });
  }
  if (body.policyApproved !== true || body.verifiedRoute !== true) {
    return json(403, { error: 'Policy approval and a verified business contact route are required.' });
  }
  try {
    const suppressed = await kvCmd('HGET', 'agency:email-suppression', toAddress);
    if (suppressed) return json(409, { error: 'Recipient is suppressed.' });

    const resultKey = `growth-os:mail:result:${idempotencyKey}`;
    const existing = await kvCmd('GET', resultKey);
    if (existing) return json(200, JSON.parse(existing));
    const lockKey = `growth-os:mail:lock:${idempotencyKey}`;
    const locked = await kvCmd('SET', lockKey, String(Date.now()), 'NX', 'EX', '300');
    if (!locked) return json(409, { error: 'This message is already being processed.' });

    let dailyKey = '';
    if (kind === 'new') {
      dailyKey = `growth-os:mail:new:${new Date().toISOString().slice(0, 10)}`;
      const count = Number(await kvCmd('INCR', dailyKey));
      if (count === 1) await kvCmd('EXPIRE', dailyKey, '172800');
      if (count > DAILY_NEW_LIMIT) {
        await Promise.all([kvCmd('DECR', dailyKey), kvCmd('DEL', lockKey)]);
        return json(429, { error: `Daily new-recipient ceiling reached (${DAILY_NEW_LIMIT}).` });
      }
    }

    try {
      const sent = await sendZohoEmail(PROJECT_ID, zohoMessage(toAddress, subject, content, mailFormat, kind === 'reply' ? body.replyToMessageId : ''));
      const result = { id: sent.messageId, acceptedAt: new Date(sent.sentAt).toISOString(), sender: sent.fromEmail };
      await Promise.all([kvCmd('SET', resultKey, JSON.stringify(result), 'EX', '604800'), kvCmd('DEL', lockKey)]);
      return json(200, result);
    } catch (error) {
      if (dailyKey) await kvCmd('DECR', dailyKey);
      await kvCmd('DEL', lockKey);
      throw error;
    }
  } catch {
    return json(502, { error: 'Lofts Mail could not process this message.' });
  }
}
