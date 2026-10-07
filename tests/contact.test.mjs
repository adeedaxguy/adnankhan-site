import test from 'node:test';
import assert from 'node:assert/strict';

process.env.ADMIN_SECRET = 'contact-test-secret';
process.env.KV_REST_API_URL = 'https://kv.contact.test';
process.env.KV_REST_API_TOKEN = 'test-token';
process.env.CONTACT_EMAIL = 'team@lofts.studio';
process.env.ZOHO_CLIENT_ID = 'zoho-test-client';
process.env.ZOHO_CLIENT_SECRET = 'zoho-test-secret';
process.env.ZOHO_FROM_EMAIL = 'hi@lofts.studio';
process.env.TURNSTILE_SECRET_KEY = 'turnstile-test-secret';

const strings = new Map();
const hashes = new Map();
const lists = new Map();
const delivered = [];
const notifications = [];
const verificationRequests = [];
let failSubmissionWrite = false;
let failOutboxWrite = false;
let holdMail = null;

function hash(key) {
  if (!hashes.has(key)) hashes.set(key, new Map());
  return hashes.get(key);
}

function command(args) {
  const [name, key, ...rest] = args;
  if (name === 'GET') return strings.get(key) ?? null;
  if (name === 'HGET') return hash(key).get(rest[0]) ?? null;
  if (name === 'HSET') {
    if (key === 'lofts:contact:outbox' && failOutboxWrite) throw new Error('Temporary queue outage');
    hash(key).set(rest[0], rest[1]); return 1;
  }
  if (name === 'HDEL') return hash(key).delete(rest[0]) ? 1 : 0;
  if (name === 'HGETALL') return [...hash(key)].flat();
  if (name === 'HKEYS') return [...hash(key).keys()];
  if (name === 'SET') {
    if (rest.includes('NX') && strings.has(key)) return null;
    strings.set(key, rest[0]);
    return 'OK';
  }
  if (name === 'INCR') {
    const value = Number(strings.get(key) || 0) + 1;
    strings.set(key, String(value));
    return value;
  }
  if (name === 'EXPIRE') return 1;
  if (name === 'DEL') return strings.delete(key) ? 1 : 0;
  if (name === 'LPUSH') {
    if (key === 'lofts:submissions' && failSubmissionWrite) throw new Error('Temporary storage outage');
    if (!lists.has(key)) lists.set(key, []);
    lists.get(key).unshift(rest[0]);
    return lists.get(key).length;
  }
  throw new Error(`Unhandled test command: ${name}`);
}

globalThis.fetch = async (input, init = {}) => {
  const url = String(input);
  if (url === 'https://challenges.cloudflare.com/turnstile/v0/siteverify') {
    const params = new URLSearchParams(init.body);
    verificationRequests.push(params);
    if (params.get('response') === 'unavailable-token') return Response.json({}, { status: 503 });
    return Response.json({
      success: params.get('response') !== 'invalid-token',
      hostname: params.get('response') === 'wrong-host-token' ? 'another.site' : 'lofts.studio',
      action: params.get('response') === 'wrong-action-token' ? 'other_action' : 'lofts_lead',
    });
  }
  if (url === 'https://kv.contact.test') {
    return Response.json({ result: command(JSON.parse(init.body)) });
  }
  if (url === 'https://accounts.zoho.com/oauth/v2/token') {
    return Response.json({ access_token: 'zoho-access-test', refresh_token: 'zoho-refresh-test', expires_in: 3600 });
  }
  if (url === 'https://mail.zoho.com/api/accounts') {
    return Response.json({ data: [{ accountId: 'zoho-account-test', primaryEmailAddress: 'hi@lofts.studio' }] });
  }
  if (url === 'https://mail.zoho.com/api/accounts/zoho-account-test/messages') {
    if (holdMail) await holdMail;
    const message = JSON.parse(init.body);
    if (message.toAddress === 'lead@acme.co') {
      delivered.push(message);
    } else {
      notifications.push(message);
    }
    return Response.json({ data: { messageId: `zoho-${delivered.length}` } });
  }
  throw new Error(`Unexpected network request: ${url}`);
};

const { default: contactHandler } = await import('../api/contact.js');

function request(payload, ip = '198.51.100.42') {
  return new Request('https://lofts.studio/api/contact', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-forwarded-for': ip,
      'x-vercel-ip-country': 'US',
    },
    body: JSON.stringify({ 'cf-turnstile-response': 'valid-token', ...payload }),
  });
}

function backgroundContext() {
  const jobs = [];
  return { waitUntil: job => jobs.push(job), drain: () => Promise.all(jobs) };
}

test('contact validation and honeypot reject bad traffic before storage', async () => {
  const invalid = await contactHandler(request({ name: 'Jane', email: 'not-an-email' }));
  assert.equal(invalid.status, 400);
  const missingPhone = await contactHandler(request({ name: 'Jane', email: 'jane@example.com' }));
  assert.equal(missingPhone.status, 400);
  const malformedPhone = await contactHandler(request({ name: 'Jane', email: 'jane@example.com', phone: '123' }));
  assert.equal(malformedPhone.status, 400);
  const fictionalPhone = await contactHandler(request({ name: 'Jane', email: 'jane@example.com', phone: '+1 202 555 0147' }));
  assert.equal(fictionalPhone.status, 400);
  const linkedName = await contactHandler(request({ name: 'Promotion https://spam.example', email: 'promoter@example.com', phone: '+1 202 555 0202' }));
  assert.equal(linkedName.status, 400);

  const bot = await contactHandler(request({ name: 'Bot', email: 'bot@example.com', _gotcha: 'filled' }));
  assert.equal(bot.status, 200);
  assert.equal(lists.get('lofts:submissions'), undefined);
});

test('contact rejects missing, failed, or mismatched verification without enrolling a lead', async () => {
  const base = { name: 'Alex Founder', email: 'alex@example.com', phone: '+44 20 7946 0958' };
  const before = lists.get('lofts:submissions')?.length || 0;
  for (const [index, token] of ['', 'invalid-token', 'wrong-host-token', 'wrong-action-token', 'unavailable-token'].entries()) {
    const response = await contactHandler(request({ ...base, 'cf-turnstile-response': token, _submissionId: `rejected-${index}` }, `198.51.100.${50 + index}`));
    assert.equal(response.status, token === 'unavailable-token' ? 503 : 400);
    assert.equal(strings.has(`lofts:contact:submission:rejected-${index}`), false);
  }
  assert.equal(lists.get('lofts:submissions')?.length || 0, before);
  assert.equal(verificationRequests.length, 4);
  assert.ok(verificationRequests.every(params => params.get('secret') === 'turnstile-test-secret' && params.get('remoteip')));
});

test('contact fails closed when its private verification key is unavailable', async () => {
  const secret = process.env.TURNSTILE_SECRET_KEY;
  delete process.env.TURNSTILE_SECRET_KEY;
  try {
    const response = await contactHandler(request({
      name: 'Alex Founder', email: 'alex@example.com', phone: '+44 20 7946 0958', _submissionId: 'missing-turnstile-secret',
    }, '198.51.100.66'));
    assert.equal(response.status, 503);
    assert.equal(strings.has('lofts:contact:submission:missing-turnstile-secret'), false);
  } finally {
    process.env.TURNSTILE_SECRET_KEY = secret;
  }
});

test('contact lead persists before a failed notification and duplicate is idempotent', async () => {
  const payload = {
    name: 'Jane Founder',
    email: 'Jane@Example.com',
    phone: '+1 202 555 0200',
    website: '',
    bottleneck: 'Paid ad landing page (Meta/Google)',
    timezone: 'America/Los_Angeles',
    source: 'landing-page-sprint-callback',
    _startedAt: Date.now() - 5000,
    _submissionId: 'submission-1',
  };

  const first = await contactHandler(request(payload));
  const firstBody = await first.json();
  assert.equal(first.status, 200);
  assert.equal(firstBody.followUp, 'queued');
  assert.equal(hash('lofts:contact:delivery:submission-1').get('reply'), 'review');
  assert.equal(lists.get('lofts:submissions').length, 1);
  assert.equal(JSON.parse(lists.get('lofts:submissions')[0]).email, 'jane@example.com');
  assert.equal(JSON.parse(lists.get('lofts:submissions')[0]).phone, '+1 202 555 0200');
  assert.equal(JSON.parse(lists.get('lofts:submissions')[0]).timezone, 'America/Los_Angeles');
  assert.equal(JSON.parse(lists.get('lofts:submissions')[0])['cf-turnstile-response'], undefined);

  const checksBeforeDuplicate = verificationRequests.length;
  const duplicate = await contactHandler(request(payload));
  assert.equal(duplicate.status, 200);
  assert.equal((await duplicate.json()).message, 'Already received');
  assert.equal(lists.get('lofts:submissions').length, 1);
  assert.equal(verificationRequests.length, checksBeforeDuplicate);
});

test('a failed lead write can be retried with the same submission ID', async () => {
  const payload = {
    name: 'Mira Founder',
    email: 'mira@example.org',
    phone: '+1 202 555 0201',
    timezone: 'Invalid/Zone',
    source: 'contact-form',
    _submissionId: 'retry-submission-1',
  };
  failSubmissionWrite = true;
  try {
    const failed = await contactHandler(request(payload, '198.51.100.44'));
    assert.equal(failed.status, 503);
    assert.equal(strings.has('lofts:contact:submission:retry-submission-1'), false);
  } finally {
    failSubmissionWrite = false;
  }

  const retried = await contactHandler(request({ ...payload, 'cf-turnstile-response': 'fresh-retry-token' }, '198.51.100.44'));
  assert.equal(retried.status, 200);
  const retriedBody = await retried.json();
  assert.equal(retriedBody.message, 'Received');
  assert.equal(retriedBody.followUp, 'queued');
  assert.equal(lists.get('lofts:submissions').length, 2);
  assert.equal(JSON.parse(lists.get('lofts:submissions')[0]).timezone, undefined);
});

test('a real project enquiry gets one tailored reply and a booking link', async () => {
  const zoho = await import('../api/_lib/zoho.js');
  const authUrl = await zoho.createZohoAuthorization('lofts-studio', 'https://lofts.studio');
  await zoho.completeZohoAuthorization('test-code', new URL(authUrl).searchParams.get('state'));
  const payload = {
    name: 'Sam Rivera',
    email: 'lead@acme.co',
    phone: '+44 20 7946 0958',
    focus: 'Improve SEO, AEO, structure, or rankings',
    message: 'Our service pages are not getting qualified search enquiries.',
    source: 'contact-form',
    _submissionId: 'submission-2',
  };
  const context = backgroundContext();
  let releaseMail;
  holdMail = new Promise(resolve => { releaseMail = resolve; });
  const response = await contactHandler(request(payload, '198.51.100.43'), context);
  assert.equal(response.status, 200);
  assert.equal((await response.json()).followUp, 'queued');
  assert.equal(lists.get('lofts:submissions').length, 3);
  assert.equal(delivered.length, 0);
  assert.equal(hash('lofts:contact:outbox').has('submission-2'), true);
  releaseMail();
  await context.drain();
  holdMail = null;
  assert.equal(hash('lofts:contact:outbox').has('submission-2'), false);
  assert.deepEqual(notifications.map(message => message.toAddress).sort(), ['adnan.toprated@gmail.com', 'adnan.webexpert@gmail.com', 'hi@lofts.studio']);
  assert.equal(delivered.length, 1);
  assert.match(delivered[0].content, /seo|rankings/i);
  assert.match(delivered[0].content, /\/book\/\?t=/);
  assert.equal(delivered[0].fromAddress, 'hi@lofts.studio');
  assert.equal(delivered[0].toAddress, 'lead@acme.co');
  assert.equal(delivered[0].isSchedule, true);
  assert.equal(delivered[0].scheduleType, 6);
  assert.equal(delivered[0].timeZone, 'GMT 5:30 (India Standard Time - Asia/Calcutta)');
  const [month, day, year, hour, minute, second] = delivered[0].scheduleTime.match(/\d+/g).map(Number);
  const delay = Date.UTC(year, month - 1, day, hour, minute, second) - 5.5 * 3600000 - Date.now();
  assert.ok(delay >= 59000 && delay <= 10 * 60000);
  assert.doesNotMatch(delivered[0].content, /gmail\.com|noreply@lofts\.studio/i);
  await contactHandler(request(payload, '198.51.100.43'));
  assert.equal(delivered.length, 1);
});

test('queued work is recovered without repeating a delivered notification', async () => {
  const saved = lists.get('lofts:submissions').map(item => JSON.parse(item)).find(item => item._id === 'submission-2');
  hash('lofts:contact:outbox').set(saved._id, JSON.stringify({
    lead: saved, subject: saved._subject, origin: 'https://lofts.studio',
  }));
  const before = notifications.length;
  const { processPendingContacts } = await import('../api/contact.js');
  const result = await processPendingContacts();
  assert.equal(result.errors, 0);
  assert.equal(hash('lofts:contact:outbox').has(saved._id), false);
  assert.equal(notifications.length, before);
});

test('the recovery job processes a stored enquiry after background work is lost', async () => {
  const lead = {
    _id: 'recovery-newsletter', _projectId: 'lofts-studio',
    name: '', email: 'subscriber@acme.co', source: 'footer-newsletter',
  };
  hash('lofts:contact:outbox').set(lead._id, JSON.stringify({
    lead, subject: 'New subscriber - subscriber@acme.co', origin: 'https://lofts.studio',
  }));
  const before = notifications.length;
  const { processPendingContacts } = await import('../api/contact.js');
  const result = await processPendingContacts();
  assert.equal(result.checked, 1);
  assert.equal(result.errors, 0);
  assert.equal(notifications.length, before + 3);
  assert.equal(hash('lofts:contact:outbox').has(lead._id), false);
});

test('an unavailable queue falls back to attempting delivery after saving the lead', async () => {
  const before = notifications.length;
  failOutboxWrite = true;
  try {
    const response = await contactHandler(request({
      name: 'Pat Founder', email: 'pat@example.com', phone: '+44 20 7946 0958',
      source: 'contact-form', _submissionId: 'outbox-unavailable-1',
    }, '198.51.100.75'));
    assert.equal(response.status, 200);
    assert.equal((await response.json()).followUp, 'attempted');
    assert.equal(notifications.length, before + 3);
    assert.equal(hash('lofts:contact:outbox').has('outbox-unavailable-1'), false);
  } finally {
    failOutboxWrite = false;
  }
});

test('newsletter form data also requires verification before storage', async () => {
  const form = new FormData();
  form.set('email', 'subscriber@example.com');
  form.set('source', 'footer-newsletter');
  form.set('_submissionId', 'newsletter-verified-1');
  form.set('cf-turnstile-response', 'newsletter-token');
  const response = await contactHandler(new Request('https://lofts.studio/api/contact', {
    method: 'POST',
    headers: { 'x-forwarded-for': '198.51.100.70' },
    body: form,
  }));
  assert.equal(response.status, 200);
  const saved = JSON.parse(lists.get('lofts:submissions')[0]);
  assert.equal(saved.email, 'subscriber@example.com');
  assert.equal(saved.source, 'footer-newsletter');
  assert.equal(saved['cf-turnstile-response'], undefined);
});
