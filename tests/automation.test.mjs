import test from 'node:test';
import assert from 'node:assert/strict';

process.env.ADMIN_SECRET = 'test-admin-secret';
process.env.KV_REST_API_URL = 'https://kv.test';
process.env.KV_REST_API_TOKEN = 'test-token';

const strings = new Map();
const hashes = new Map();
const sets = new Map();
const lists = new Map();

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
  if (name === 'HDEL') return hash(key).delete(rest[0]) ? 1 : 0;
  if (name === 'SADD') {
    if (!sets.has(key)) sets.set(key, new Set());
    const before = sets.get(key).size;
    sets.get(key).add(rest[0]);
    return sets.get(key).size > before ? 1 : 0;
  }
  if (name === 'SET') {
    const nx = rest.includes('NX');
    if (nx && strings.has(key)) return null;
    strings.set(key, rest[0]);
    return 'OK';
  }
  if (name === 'MGET') return [key, ...rest].map(item => strings.get(item) ?? null);
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
  if (url === 'https://kv.test') {
    const args = JSON.parse(init.body);
    return Response.json({ result: command(args) });
  }
  if (url.startsWith('https://example-business.test')) {
    return new Response('<html><head><title>Example Services</title></head><body><h1>Welcome to our website</h1><p>We help companies grow.</p></body></html>', {
      status: 200,
      headers: { 'content-type': 'text/html' },
    });
  }
  throw new Error(`Unexpected network request: ${url}`);
};

const automation = await import('../api/_lib/automation.js');

test('signed automation tokens reject tampering and wrong actions', async () => {
  const token = await automation.signAutomationToken({ a: 'book', p: 'lofts-studio', l: 'lead-1', exp: Date.now() + 60000 });
  assert.equal((await automation.verifyAutomationToken(token, 'book')).l, 'lead-1');
  assert.equal(await automation.verifyAutomationToken(`${token}x`, 'book'), null);
  assert.equal(await automation.verifyAutomationToken(token, 'unsubscribe'), null);
});

test('lead enrolment stores evidence-based analysis and remains in review mode', async () => {
  const sequence = await automation.enrollLeadAutomation({
    _id: 'lead-1',
    _projectId: 'lofts-studio',
    _ts: Date.now(),
    name: 'Jane Founder',
    email: 'jane@example-business.test',
    website: 'https://example-business.test',
    bottleneck: 'Paid ad landing page (Meta/Google)',
    source: 'landing-page-sprint-callback',
    nurtureConsent: 'no',
  });
  assert.equal(sequence.status, 'review');
  assert.equal(sequence.steps.length, 8);
  assert.equal(sequence.analysis.status, 'reviewed');
  assert.match(sequence.analysis.observations.join(' '), /heading|lead form|proof/i);
});

test('booking slots are timezone-backed and one slot cannot be reserved twice', async () => {
  const token = await automation.signAutomationToken({ a: 'book', p: 'lofts-studio', l: 'lead-1', exp: Date.now() + 30 * 86400000 });
  const availability = await automation.getAvailableSlots(token);
  assert.ok(availability.slots.length > 0);
  assert.equal(availability.timezone, 'Asia/Karachi');
  const first = await automation.createBooking(token, { start: availability.slots[0], timezone: 'Europe/London' });
  assert.equal(first.booking.status, 'confirmed');
  await assert.rejects(
    automation.createBooking(token, { start: availability.slots[0], timezone: 'Europe/London' }),
    /no longer available|just booked/i,
  );
  const sequence = await automation.getSequence('lofts-studio', 'lead-1');
  assert.equal(sequence.status, 'booked');
});

test('unsubscribe creates a durable suppression and stops the sequence', async () => {
  const token = await automation.signAutomationToken({ a: 'unsubscribe', p: 'lofts-studio', l: 'lead-1', s: 'first-response', exp: Date.now() + 60000 });
  await automation.unsubscribeLead(token);
  const sequence = await automation.getSequence('lofts-studio', 'lead-1');
  assert.equal(sequence.status, 'unsubscribed');
  assert.ok(hash('agency:email-suppression').has('jane@example-business.test'));
});

test('manual CRM email creates a review-only sequence when global automation is active', async () => {
  hash('agency:automation-config').set('lofts-studio', JSON.stringify({
    mode: 'active',
    complianceAddress: '1 Test Street, Multan, Pakistan',
  }));
  const rendered = await automation.buildCrmEmail('lofts-studio', {
    id: 'lead-manual',
    _ts: Date.now(),
    name: 'Manual Prospect',
    email: 'manual@prospect.co',
    source: 'contact-form',
  }, 'A direct reply', 'Thanks for your enquiry.', 'https://lofts.studio');
  const sequence = await automation.getSequence('lofts-studio', 'lead-manual');
  assert.equal(sequence.status, 'review');
  assert.match(rendered.html, /Book a call|Choose a call time/);
  assert.match(rendered.text, /Stop follow-ups/);
});
