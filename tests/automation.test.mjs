import test from 'node:test';
import assert from 'node:assert/strict';

process.env.ADMIN_SECRET = 'test-admin-secret';
process.env.KV_REST_API_URL = 'https://kv.test';
process.env.KV_REST_API_TOKEN = 'test-token';
process.env.RESEND_API_KEY = 'resend-test-key';
process.env.CONTACT_EMAIL = 'team@lofts.studio';
process.env.CONTACT_EMAIL_BCC = 'owner@lofts.studio';
process.env.ZOHO_CLIENT_ID = 'zoho-test-client';
process.env.ZOHO_CLIENT_SECRET = 'zoho-test-secret';
process.env.ZOHO_FROM_EMAIL = 'hi@lofts.studio';
process.env.GOOGLE_CALENDAR_CLIENT_ID = 'google-test-client';
process.env.GOOGLE_CALENDAR_CLIENT_SECRET = 'google-test-secret';
process.env.GOOGLE_CALENDAR_EMAIL = 'owner@lofts.studio';

const strings = new Map();
const hashes = new Map();
const sets = new Map();
const lists = new Map();
const sentEmails = [];
const calendarEvents = [];
const googleCalendarEvents = [];
const deletedGoogleEvents = [];
let calendarBusyStart = '';
let googleBusyStart = '';
let failZohoEvent = false;
let failGoogleDelete = false;

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
  if (name === 'DEL') return strings.delete(key) ? 1 : 0;
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
  if (url === 'https://api.resend.com/emails') {
    sentEmails.push(JSON.parse(init.body));
    return Response.json({ id: `message-${sentEmails.length}` });
  }
  if (url === 'https://accounts.zoho.com/oauth/v2/token') {
    return Response.json({ access_token: 'zoho-access-test', refresh_token: 'zoho-refresh-test', expires_in: 3600 });
  }
  if (url === 'https://mail.zoho.com/api/accounts') {
    return Response.json({ data: [{ accountId: 'zoho-account-test', primaryEmailAddress: 'hi@lofts.studio' }] });
  }
  if (url.startsWith('https://calendar.zoho.com/api/v1/calendars/freebusy')) {
    const stamp = value => new Date(value).toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
    return Response.json({ freebusy: calendarBusyStart ? [{ startTime: stamp(calendarBusyStart), endTime: stamp(new Date(new Date(calendarBusyStart).getTime() + 1800000)), fbtype: 'busy' }] : [] });
  }
  if (url === 'https://calendar.zoho.com/api/v1/calendars/primary') {
    return Response.json({ calendars: [{ uid: 'primary-test-calendar' }] });
  }
  if (url.startsWith('https://calendar.zoho.com/api/v1/calendars/primary-test-calendar/events')) {
    if (failZohoEvent) return Response.json({ status: { description: 'Zoho Calendar is unavailable.' } }, { status: 503 });
    calendarEvents.push(JSON.parse(new URL(url).searchParams.get('eventdata')));
    return Response.json({ events: [{ uid: `event-${calendarEvents.length}` }] });
  }
  if (url === 'https://oauth2.googleapis.com/token') {
    return Response.json({ access_token: 'google-access-test', refresh_token: 'google-refresh-test', expires_in: 3600 });
  }
  if (url === 'https://openidconnect.googleapis.com/v1/userinfo') {
    return Response.json({ email: 'owner@lofts.studio', email_verified: true });
  }
  if (url === 'https://www.googleapis.com/calendar/v3/freeBusy') {
    return Response.json({ calendars: { primary: { busy: googleBusyStart ? [{ start: googleBusyStart, end: new Date(new Date(googleBusyStart).getTime() + 1800000).toISOString() }] : [] } } });
  }
  if (url === 'https://www.googleapis.com/calendar/v3/calendars/primary/events' && init.method === 'POST') {
    const event = JSON.parse(init.body);
    googleCalendarEvents.push(event);
    return Response.json({ id: event.id, htmlLink: `https://calendar.google.com/event/${event.id}` });
  }
  if (url.startsWith('https://www.googleapis.com/calendar/v3/calendars/primary/events/') && init.method === 'DELETE') {
    if (failGoogleDelete) return Response.json({ error: { message: 'Google Calendar could not remove the event.' } }, { status: 503 });
    deletedGoogleEvents.push(url.split('/').at(-1));
    return new Response(null, { status: 204 });
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
    phone: '+1 202 555 0147',
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
  await assert.rejects(automation.createBooking(token, { start: availability.slots[0], phone: 'abc' }), /valid phone/i);
  const first = await automation.createBooking(token, { start: availability.slots[0], timezone: 'Europe/London' });
  assert.equal(first.booking.status, 'requested');
  assert.equal(first.booking.calendarStatus, 'not-connected');
  assert.equal((await automation.getAvailableSlots(token)).booking.id, first.booking.id);
  assert.equal(sentEmails.length, 2);
  assert.ok(sentEmails.some(email => email.to.includes('team@lofts.studio')));
  assert.ok(sentEmails.some(email => email.to.includes('owner@lofts.studio')));
  assert.ok(sentEmails.some(email => email.to.includes('jane@example-business.test')));
  const repeat = await automation.createBooking(token, { start: availability.slots[1], timezone: 'Europe/London' });
  assert.equal(repeat.booking.id, first.booking.id);
  await automation.enrollLeadAutomation({ _id: 'lead-2', _projectId: 'lofts-studio', name: 'Second Lead', email: 'second@example.com', phone: '+1 202 555 0148' });
  const secondToken = await automation.signAutomationToken({ a: 'book', p: 'lofts-studio', l: 'lead-2', exp: Date.now() + 30 * 86400000 });
  await assert.rejects(
    automation.createBooking(secondToken, { start: availability.slots[0], timezone: 'Europe/London' }),
    /no longer available|just booked/i,
  );
  delete process.env.CONTACT_EMAIL_BCC;
  await assert.rejects(automation.getAvailableSlots(secondToken), /booking is unavailable/i);
  process.env.CONTACT_EMAIL_BCC = 'owner@lofts.studio';
  const sequence = await automation.getSequence('lofts-studio', 'lead-1');
  assert.equal(sequence.status, 'booked');
});

test('fallback first reply acknowledges a free-text enquiry without a model', async () => {
  const { fallbackLeadReply } = await import('../api/_lib/lead-reply.js');
  const reply = fallbackLeadReply({ name: 'Mina Patel', message: 'Our Shopify checkout is losing mobile customers.' });
  assert.match(reply.body, /Shopify checkout is losing mobile customers/);
});

test('connected Zoho and Google calendars filter busy times and create both events', async () => {
  const zoho = await import('../api/_lib/zoho.js');
  const authUrl = await zoho.createZohoAuthorization('lofts-studio', 'https://lofts.studio');
  await zoho.completeZohoAuthorization('test-code', new URL(authUrl).searchParams.get('state'));
  const lead = await automation.enrollLeadAutomation({
    _id: 'lead-calendar', _projectId: 'lofts-studio', name: 'Calendar Lead',
    email: 'calendar@prospect.co', phone: '+1 202 555 0150',
  });
  assert.equal(lead.leadId, 'lead-calendar');
  const token = await automation.signAutomationToken({ a: 'book', p: 'lofts-studio', l: 'lead-calendar', exp: Date.now() + 30 * 86400000 });
  const firstAvailability = await automation.getAvailableSlots(token);
  assert.equal(firstAvailability.calendarConnected, false);
  const google = await import('../api/_lib/google-calendar.js');
  const googleAuthUrl = await google.createGoogleCalendarAuthorization('lofts-studio', 'https://lofts.studio');
  await google.completeGoogleCalendarAuthorization('test-code', new URL(googleAuthUrl).searchParams.get('state'));
  calendarBusyStart = firstAvailability.slots[0];
  googleBusyStart = firstAvailability.slots[1];
  const availability = await automation.getAvailableSlots(token);
  assert.equal(availability.calendarConnected, true);
  assert.ok(!availability.slots.includes(calendarBusyStart));
  assert.ok(!availability.slots.includes(googleBusyStart));
  const result = await automation.createBooking(token, { start: availability.slots[0], timezone: 'America/New_York' });
  assert.equal(result.booking.status, 'confirmed');
  assert.equal(result.booking.calendarEventUid, 'event-1');
  assert.equal(result.booking.googleEventId, googleCalendarEvents[0].id);
  assert.equal(calendarEvents.length, 1);
  assert.equal(googleCalendarEvents.length, 1);
  assert.equal(calendarEvents[0].notify_attendee, 1);
  assert.deepEqual(calendarEvents[0].attendees.map(item => item.email).sort(), ['calendar@prospect.co', 'team@lofts.studio']);
  assert.ok(sentEmails.some(email => email.to.includes('calendar@prospect.co') && /confirmed/i.test(email.subject)));
});

test('a failed Zoho event rolls back the Google event', async () => {
  await automation.enrollLeadAutomation({
    _id: 'lead-rollback', _projectId: 'lofts-studio', name: 'Rollback Lead',
    email: 'rollback@prospect.co', phone: '+1 202 555 0151',
  });
  const token = await automation.signAutomationToken({ a: 'book', p: 'lofts-studio', l: 'lead-rollback', exp: Date.now() + 30 * 86400000 });
  const availability = await automation.getAvailableSlots(token);
  failZohoEvent = true;
  const result = await automation.createBooking(token, { start: availability.slots[0] });
  failZohoEvent = false;
  assert.equal(result.booking.status, 'requested');
  assert.equal(result.booking.calendarStatus, 'zoho-review');
  assert.equal(deletedGoogleEvents.at(-1), googleCalendarEvents.at(-1).id);
  assert.equal((await automation.getAvailableSlots(token)).booking.id, result.booking.id);
});

test('failed rollback stays a request and preserves the occupied time', async () => {
  await automation.enrollLeadAutomation({
    _id: 'lead-partial', _projectId: 'lofts-studio', name: 'Partial Lead',
    email: 'partial@prospect.co', phone: '+1 202 555 0152',
  });
  const token = await automation.signAutomationToken({ a: 'book', p: 'lofts-studio', l: 'lead-partial', exp: Date.now() + 30 * 86400000 });
  const availability = await automation.getAvailableSlots(token);
  failZohoEvent = true;
  failGoogleDelete = true;
  const result = await automation.createBooking(token, { start: availability.slots[0] });
  failZohoEvent = false;
  failGoogleDelete = false;
  assert.equal(result.booking.status, 'requested');
  assert.equal(result.booking.calendarStatus, 'partial-google');
  assert.equal((await automation.getAvailableSlots(token)).booking.id, result.booking.id);
  assert.ok(sentEmails.some(email => email.to.includes('owner@lofts.studio') && /Zoho needs review/.test(email.text)));
});

test('changing the Google account invalidates the old calendar connection', async () => {
  const google = await import('../api/_lib/google-calendar.js');
  await google.saveGoogleCalendarClient('lofts-studio', {
    clientId: 'google-test-client', clientSecret: 'google-test-secret', expectedEmail: 'new-owner@lofts.studio',
  });
  assert.equal((await google.getGoogleCalendarStatus('lofts-studio')).connected, false);
  const authUrl = await google.createGoogleCalendarAuthorization('lofts-studio', 'https://lofts.studio');
  await assert.rejects(
    google.completeGoogleCalendarAuthorization('test-code', new URL(authUrl).searchParams.get('state')),
    /Sign in with new-owner@lofts.studio/,
  );
});

test('paused automation does not send an immediate lead reply', async () => {
  hash('agency:automation-config').set('lofts-studio', JSON.stringify({ mode: 'paused' }));
  const sequence = await automation.enrollLeadAutomation({
    _id: 'lead-paused', _projectId: 'lofts-studio', name: 'Paused Lead',
    email: 'paused@prospect.co', phone: '+1 202 555 0149',
  });
  const sentBefore = sentEmails.length;
  assert.deepEqual(await automation.sendInboundReply(sequence), { status: 'skipped' });
  assert.equal(sentEmails.length, sentBefore);
  hash('agency:automation-config').delete('lofts-studio');
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
