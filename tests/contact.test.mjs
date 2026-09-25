import test from 'node:test';
import assert from 'node:assert/strict';

process.env.ADMIN_SECRET = 'contact-test-secret';
process.env.KV_REST_API_URL = 'https://kv.contact.test';
process.env.KV_REST_API_TOKEN = 'test-token';
process.env.CONTACT_EMAIL = 'team@lofts.studio';
process.env.ZOHO_CLIENT_ID = 'zoho-test-client';
process.env.ZOHO_CLIENT_SECRET = 'zoho-test-secret';
process.env.ZOHO_FROM_EMAIL = 'hi@lofts.studio';

const strings = new Map();
const hashes = new Map();
const lists = new Map();
const delivered = [];
const notifications = [];
let failSubmissionWrite = false;

function hash(key) {
  if (!hashes.has(key)) hashes.set(key, new Map());
  return hashes.get(key);
}

function command(args) {
  const [name, key, ...rest] = args;
  if (name === 'HGET') return hash(key).get(rest[0]) ?? null;
  if (name === 'HSET') { hash(key).set(rest[0], rest[1]); return 1; }
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
    body: JSON.stringify(payload),
  });
}

test('contact validation and honeypot reject bad traffic before storage', async () => {
  const invalid = await contactHandler(request({ name: 'Jane', email: 'not-an-email' }));
  assert.equal(invalid.status, 400);
  const missingPhone = await contactHandler(request({ name: 'Jane', email: 'jane@example.com' }));
  assert.equal(missingPhone.status, 400);
  const malformedPhone = await contactHandler(request({ name: 'Jane', email: 'jane@example.com', phone: '123' }));
  assert.equal(malformedPhone.status, 400);

  const bot = await contactHandler(request({ name: 'Bot', email: 'bot@example.com', _gotcha: 'filled' }));
  assert.equal(bot.status, 200);
  assert.equal(lists.get('lofts:submissions'), undefined);
});

test('contact lead persists before a failed notification and duplicate is idempotent', async () => {
  const payload = {
    name: 'Jane Founder',
    email: 'Jane@Example.com',
    phone: '+1 202 555 0147',
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
  assert.equal(firstBody.notification, 'delayed');
  assert.equal(firstBody.automation, 'review');
  assert.equal(lists.get('lofts:submissions').length, 1);
  assert.equal(JSON.parse(lists.get('lofts:submissions')[0]).email, 'jane@example.com');
  assert.equal(JSON.parse(lists.get('lofts:submissions')[0]).phone, '+1 202 555 0147');
  assert.equal(JSON.parse(lists.get('lofts:submissions')[0]).timezone, 'America/Los_Angeles');

  const duplicate = await contactHandler(request(payload));
  assert.equal(duplicate.status, 200);
  assert.equal((await duplicate.json()).message, 'Already received');
  assert.equal(lists.get('lofts:submissions').length, 1);
});

test('a failed lead write can be retried with the same submission ID', async () => {
  const payload = {
    name: 'Mira Founder',
    email: 'mira@example.org',
    phone: '+1 202 555 0199',
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

  const retried = await contactHandler(request(payload, '198.51.100.44'));
  assert.equal(retried.status, 200);
  const retriedBody = await retried.json();
  assert.equal(retriedBody.message, 'Received');
  assert.equal(retriedBody.reply, 'delayed');
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
  const response = await contactHandler(request(payload, '198.51.100.43'));
  assert.equal(response.status, 200);
  assert.equal((await response.json()).reply, 'scheduled');
  assert.deepEqual(notifications.map(message => message.toAddress), ['hi@lofts.studio', 'adnan.webexpert@gmail.com']);
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
