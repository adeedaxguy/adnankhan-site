import test from 'node:test';
import assert from 'node:assert/strict';

process.env.ADMIN_SECRET = 'contact-test-secret';
process.env.KV_REST_API_URL = 'https://kv.contact.test';
process.env.KV_REST_API_TOKEN = 'test-token';
process.env.CONTACT_EMAIL = 'team@lofts.studio';
process.env.RESEND_API_KEY = 'resend-test-key';

const strings = new Map();
const hashes = new Map();
const lists = new Map();
const delivered = [];

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
  if (name === 'LPUSH') {
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
  if (url === 'https://api.resend.com/emails') {
    const message = JSON.parse(init.body);
    if (message.to?.includes('lead@acme.co')) {
      delivered.push(message);
      return Response.json({ id: 'resend-lead-1' });
    }
    return Response.json({ message: 'Temporary provider outage' }, { status: 503 });
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

  const duplicate = await contactHandler(request(payload));
  assert.equal(duplicate.status, 200);
  assert.equal((await duplicate.json()).message, 'Already received');
  assert.equal(lists.get('lofts:submissions').length, 1);
});

test('a real project enquiry gets one tailored reply and a booking link', async () => {
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
  assert.equal(delivered.length, 1);
  assert.match(delivered[0].text, /seo|rankings/i);
  assert.match(delivered[0].text, /\/book\/\?t=/);
  assert.equal(delivered[0].from, 'Lofts Studio <hi@lofts.studio>');
  assert.equal(delivered[0].reply_to, 'hi@lofts.studio');
  assert.ok(new Date(delivered[0].scheduled_at).getTime() - Date.now() >= 59000);
  assert.ok(new Date(delivered[0].scheduled_at).getTime() - Date.now() <= 10 * 60000);
  assert.doesNotMatch(delivered[0].html, /gmail\.com|noreply@lofts\.studio/i);
  await contactHandler(request(payload, '198.51.100.43'));
  assert.equal(delivered.length, 1);
});
