import test from 'node:test';
import assert from 'node:assert/strict';

process.env.ADMIN_SECRET = 'test-admin-secret';
process.env.KV_REST_API_URL = 'https://kv.test';
process.env.KV_REST_API_TOKEN = 'test-token';
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
const zohoEmails = [];
const calendarEvents = [];
const googleCalendarEvents = [];
const deletedGoogleEvents = [];
let calendarBusyStart = '';
let googleBusyStart = '';
let googleTokenScope = '';
let googleCalendarResponseKey = 'primary';
let failZohoEvent = false;
let failGoogleDelete = false;
let failScheduledZohoEmail = false;

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
  if (url === 'https://mail.zoho.com/api/accounts/zoho-account-test/messages') {
    const email = JSON.parse(init.body);
    if (failScheduledZohoEmail && email.isSchedule) {
      return Response.json({ status: { description: 'Invalid schedule' }, data: { errorCode: 'PATTERN_NOT_MATCHED' } }, { status: 400 });
    }
    zohoEmails.push(email);
    return Response.json({ data: { messageId: `message-${zohoEmails.length}` } });
  }
  if (url === 'https://accounts.zoho.com/oauth/v2/token') {
    return Response.json({ access_token: 'zoho-access-test', refresh_token: 'zoho-refresh-test', expires_in: 3600 });
  }
  if (url === 'https://mail.zoho.com/api/accounts') {
    return Response.json({ data: [{ accountId: 'zoho-account-test', primaryEmailAddress: 'hi@lofts.studio' }] });
  }
  if (url === 'https://mail.zoho.com/api/accounts/zoho-account-test/folders') {
    return Response.json({ data: [{ folderId: 'inbox-test', folderType: 'Inbox' }] });
  }
  if (url.startsWith('https://mail.zoho.com/api/accounts/zoho-account-test/messages/view')) {
    return Response.json({ data: [] });
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
    return Response.json({ access_token: 'google-access-test', refresh_token: 'google-refresh-test', expires_in: 3600, ...(googleTokenScope ? { scope: googleTokenScope } : {}) });
  }
  if (url === 'https://openidconnect.googleapis.com/v1/userinfo') {
    return Response.json({ email: 'owner@lofts.studio', email_verified: true });
  }
  if (url === 'https://www.googleapis.com/calendar/v3/freeBusy') {
    return Response.json({ calendars: { [googleCalendarResponseKey]: { busy: googleBusyStart ? [{ start: googleBusyStart, end: new Date(new Date(googleBusyStart).getTime() + 1800000).toISOString() }] : [] } } });
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
  const zoho = await import('../api/_lib/zoho.js');
  const authUrl = await zoho.createZohoAuthorization('lofts-studio', 'https://lofts.studio');
  await zoho.completeZohoAuthorization('test-code', new URL(authUrl).searchParams.get('state'));
  const config = await automation.getAutomationConfig('lofts-studio');
  assert.deepEqual(config.booking.days, [0, 1, 2, 3, 4, 5, 6]);
  assert.equal(config.booking.start, '00:00');
  assert.equal(config.booking.end, '24:00');
  assert.equal(config.booking.minimumNoticeHours, 0);
  const token = await automation.signAutomationToken({ a: 'book', p: 'lofts-studio', l: 'lead-1', exp: Date.now() + 30 * 86400000 });
  const availability = await automation.getAvailableSlots(token);
  assert.ok(availability.slots.length > 160);
  assert.equal(availability.timezone, 'Asia/Karachi');
  const localTimes = new Set(availability.slots.map(slot => new Intl.DateTimeFormat('en-GB', {
    timeZone: availability.timezone, hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
  }).format(new Date(slot))));
  assert.ok(localTimes.has('00:00'));
  assert.ok(localTimes.has('23:30'));
  assert.equal(new Set(availability.slots.map(slot => new Intl.DateTimeFormat('en-US', {
    timeZone: availability.timezone, weekday: 'short',
  }).format(new Date(slot)))).size, 7);
  await assert.rejects(automation.createBooking(token, { start: availability.slots[0], phone: 'abc' }), /valid phone/i);
  const first = await automation.createBooking(token, { start: availability.slots[0], timezone: 'Europe/London' });
  assert.equal(first.booking.status, 'requested');
  assert.equal(first.booking.calendarStatus, 'not-connected');
  assert.equal((await automation.getAvailableSlots(token)).booking.id, first.booking.id);
  assert.equal(zohoEmails.length, 3);
  assert.ok(zohoEmails.some(email => email.toAddress === 'team@lofts.studio'));
  assert.ok(zohoEmails.some(email => email.toAddress === 'owner@lofts.studio'));
  assert.ok(zohoEmails.some(email => email.toAddress === 'jane@example-business.test'));
  const repeat = await automation.createBooking(token, { start: availability.slots[1], timezone: 'Europe/London' });
  assert.equal(repeat.booking.id, first.booking.id);
  await automation.enrollLeadAutomation({ _id: 'lead-2', _projectId: 'lofts-studio', name: 'Second Lead', email: 'second@example.com', phone: '+1 202 555 0148' });
  const secondToken = await automation.signAutomationToken({ a: 'book', p: 'lofts-studio', l: 'lead-2', exp: Date.now() + 30 * 86400000 });
  await assert.rejects(
    automation.createBooking(secondToken, { start: availability.slots[0], timezone: 'Europe/London' }),
    /no longer available|just booked/i,
  );
  delete process.env.CONTACT_EMAIL_BCC;
  assert.ok((await automation.getAvailableSlots(secondToken)).slots.length > 0);
  delete process.env.CONTACT_EMAIL;
  await assert.rejects(automation.getAvailableSlots(secondToken), /booking is unavailable/i);
  process.env.CONTACT_EMAIL = 'team@lofts.studio';
  process.env.CONTACT_EMAIL_BCC = 'owner@lofts.studio';
  const sequence = await automation.getSequence('lofts-studio', 'lead-1');
  assert.equal(sequence.status, 'booked');
});

test('fallback first reply acknowledges a free-text enquiry without a model', async () => {
  const { classifyLeadEnquiry, fallbackLeadReply, leadExpertise } = await import('../api/_lib/lead-reply.js');
  const reply = fallbackLeadReply({ name: 'Mina Patel', message: 'Our Shopify checkout is losing mobile customers.' });
  assert.match(reply.body, /Shopify checkout is losing mobile customers/);
  assert.equal(classifyLeadEnquiry({ focus: 'Build or redesign a business website', message: 'The WordPress site needs a redesign.' }), 'wordpress');
  assert.equal(classifyLeadEnquiry({ bottleneck: 'Checkout flow', pageTitle: 'Shopify Development' }), 'shopify');
  assert.equal(classifyLeadEnquiry({ bottleneck: 'WordPress', sourcePath: '/services/technical-seo-audit.html' }), 'seo');
  assert.equal(classifyLeadEnquiry({ bottleneck: 'Migrating from Shopify', sourcePath: '/services/woocommerce-development.html' }), 'woocommerce');
  assert.equal(classifyLeadEnquiry({ focus: 'Build WordPress, Webflow, or a custom CMS', message: 'Our Webflow CMS needs a redesign.' }), 'webflow');
  assert.match(leadExpertise({ message: 'Our Shopify checkout is losing mobile customers.' }).join(' '), /Shopify storefronts/);
  assert.match(fallbackLeadReply({ name: 'Ari', focus: 'Improve SEO, AEO, structure, or rankings' }).body, /search visibility/i);
  assert.match(fallbackLeadReply({ name: 'Ari', focus: 'Add AI calling agents, chatbots, or automation' }).body, /automation/i);
});

test('every homepage enquiry choice routes to a relevant reply template', async () => {
  const { classifyLeadEnquiry, fallbackLeadReply } = await import('../api/_lib/lead-reply.js');
  const choices = [
    ['Audit my current website and tell me what to fix', 'audit'],
    ['Build or redesign a business website', 'website'],
    ['Build a SaaS, app, or custom web platform', 'app'],
    ['Improve SEO, AEO, structure, or rankings', 'seo'],
    ['Improve conversions, leads, or landing pages', 'conversion'],
    ['Build or improve a Shopify / WooCommerce store', 'ecommerce'],
    ['Build WordPress, Webflow, or a custom CMS', 'cms'],
    ['Add AI calling agents, chatbots, or automation', 'automation'],
    ['Something else - I will explain', 'general'],
  ];
  for (const [focus, expected] of choices) {
    assert.equal(classifyLeadEnquiry({ focus }), expected);
    assert.match(fallbackLeadReply({ name: 'Sam', focus }).body, /choose a time below/i);
  }
});

test('existing Lofts booking settings migrate to all-day availability', async () => {
  hash('agency:automation-config').set('lofts-studio', JSON.stringify({ booking: {
    enabled: false, days: [1, 2, 3, 4, 5, 6], start: '17:00', end: '22:00', minimumNoticeHours: 12,
    horizonDays: 7,
  } }));
  const config = await automation.getAutomationConfig('lofts-studio');
  assert.equal(config.booking.enabled, true);
  assert.deepEqual(config.booking.days, [0, 1, 2, 3, 4, 5, 6]);
  assert.equal(config.booking.end, '24:00');
  assert.equal(config.booking.minimumNoticeHours, 0);
  assert.equal(config.booking.horizonDays, 21);
  hash('agency:automation-config').delete('lofts-studio');
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
  assert.deepEqual(calendarEvents[0].attendees.map(item => item.email), ['calendar@prospect.co']);
  assert.ok(zohoEmails.some(email => email.toAddress === 'calendar@prospect.co' && /confirmed/i.test(email.subject)));
  assert.ok(zohoEmails.some(email => email.toAddress === 'calendar@prospect.co' && email.fromAddress === 'hi@lofts.studio'));
  assert.ok(zohoEmails.some(email => email.toAddress === 'team@lofts.studio' && /Call booked/.test(email.subject)));
  assert.ok(zohoEmails.some(email => email.toAddress === 'owner@lofts.studio' && /Call booked/.test(email.subject)));
});

test('a failed scheduled first reply records the provider error and can be previewed without starting follow-ups', async () => {
  const sequence = await automation.enrollLeadAutomation({
    _id: 'lead-preview', _projectId: 'lofts-studio', _ts: Date.now(),
    name: 'Preview Lead', email: 'preview@prospect.co', phone: '+1 202 555 0163',
    focus: 'Build or improve a Shopify / WooCommerce store',
    message: 'Our WooCommerce checkout is difficult to use on phones.',
  }, 'https://lofts.studio', { forceReview: true });
  failScheduledZohoEmail = true;
  try {
    assert.deepEqual(await automation.sendInboundReply(sequence), { status: 'delayed' });
  } finally {
    failScheduledZohoEmail = false;
  }
  const failed = await automation.getSequence('lofts-studio', 'lead-preview');
  assert.equal(failed.status, 'needs-review');
  assert.match(failed.lastError, /Invalid schedule PATTERN_NOT_MATCHED/);
  assert.equal(failed.steps[0].status, 'pending');

  const sentBefore = zohoEmails.length;
  const preview = await automation.controlSequence('lofts-studio', 'lead-preview', 'send-next');
  assert.equal(zohoEmails.length, sentBefore + 1);
  assert.equal(zohoEmails.at(-1).isSchedule, undefined);
  assert.equal(preview.steps[0].status, 'sent');
  assert.equal(preview.status, 'review');
  assert.equal(preview.lastError, null);
});

test('Google authorization allows time to review consent but still expires', async () => {
  const google = await import('../api/_lib/google-calendar.js');
  const issuedAt = Date.now();
  const authUrl = await google.createGoogleCalendarAuthorization('lofts-studio', 'https://lofts.studio');
  const state = new URL(authUrl).searchParams.get('state');
  const originalNow = Date.now;
  try {
    Date.now = () => issuedAt + 20 * 60 * 1000;
    await google.completeGoogleCalendarAuthorization('test-code', state);
    Date.now = () => issuedAt + 31 * 60 * 1000;
    await assert.rejects(google.completeGoogleCalendarAuthorization('test-code', state), /expired/i);
  } finally {
    Date.now = originalNow;
  }
});

test('Google authorization accepts equivalent email scope and resolved calendar ID', async () => {
  const google = await import('../api/_lib/google-calendar.js');
  const previousBusyStart = googleBusyStart;
  googleBusyStart = '';
  googleTokenScope = [
    'openid', 'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/calendar.freebusy',
    'https://www.googleapis.com/auth/calendar.events',
  ].join(' ');
  googleCalendarResponseKey = 'owner@lofts.studio';
  try {
    const authUrl = await google.createGoogleCalendarAuthorization('lofts-studio', 'https://lofts.studio');
    await google.completeGoogleCalendarAuthorization('test-code', new URL(authUrl).searchParams.get('state'));
    assert.equal((await google.getGoogleCalendarStatus('lofts-studio')).connected, true);
    assert.deepEqual(await google.googleBusyIntervals('lofts-studio', Date.now(), Date.now() + 3600000), []);

    googleTokenScope = 'openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar.freebusy';
    const incompleteAuthUrl = await google.createGoogleCalendarAuthorization('lofts-studio', 'https://lofts.studio');
    await assert.rejects(
      google.completeGoogleCalendarAuthorization('test-code', new URL(incompleteAuthUrl).searchParams.get('state')),
      /Grant both Google Calendar permissions/i,
    );
  } finally {
    googleTokenScope = '';
    googleCalendarResponseKey = 'primary';
    googleBusyStart = previousBusyStart;
  }
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
  assert.ok(zohoEmails.some(email => email.toAddress === 'owner@lofts.studio' && email.subject === 'Call requested: Rollback Lead'));
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
  assert.ok(zohoEmails.some(email => email.toAddress === 'owner@lofts.studio' && /Zoho needs review/.test(email.content)));
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
  const sentBefore = zohoEmails.length;
  assert.deepEqual(await automation.sendInboundReply(sequence), { status: 'skipped' });
  assert.equal(zohoEmails.length, sentBefore);
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
  assert.match(rendered.html, /Choose a time to talk/);
  assert.match(rendered.html, /mailto:hi@lofts.studio/);
  assert.match(rendered.text, /Stop follow-ups/);
  hash('agency:automation-config').delete('lofts-studio');
});

test('first lead reply uses a restrained service-specific email and Zoho sender', async () => {
  const sequence = await automation.enrollLeadAutomation({
    _id: 'lead-email-design', _projectId: 'lofts-studio', _ts: Date.now(),
    name: 'Sam Founder', email: 'sam@prospect.co', phone: '+1 202 555 0163',
    focus: 'Build or improve a Shopify / WooCommerce store',
    message: 'Our WooCommerce checkout is difficult to use on phones.',
  }, 'https://lofts.studio', { forceReview: true });
  assert.deepEqual(await automation.sendInboundReply(sequence), { status: 'scheduled' });
  const email = zohoEmails.at(-1);
  assert.equal(email.toAddress, 'sam@prospect.co');
  assert.equal(email.fromAddress, 'hi@lofts.studio');
  assert.equal(email.mailFormat, 'html');
  assert.match(email.content, /WooCommerce checkout is difficult to use on phones/);
  assert.match(email.content, /WooCommerce architecture and custom product logic/);
  assert.match(email.content, /Where we can help/);
  assert.match(email.content, /Choose a time to talk/);
  assert.match(email.content, /#a9432d/);
  assert.doesNotMatch(email.content, /adnan\.webexpert@|adnan\.toprated@|<img\b/i);
  assert.doesNotMatch(email.content, /Test Street/);
  assert.ok(email.isSchedule);
  assert.equal((await automation.getSequence('lofts-studio', 'lead-email-design')).steps[0].status, 'scheduled');
});
