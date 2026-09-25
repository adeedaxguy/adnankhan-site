const CLIENT_KEY = 'agency:google-calendar-clients';
const CONNECTION_KEY = 'agency:google-calendar-connections';
const SCOPES = [
  'openid',
  'email',
  'https://www.googleapis.com/auth/calendar.freebusy',
  'https://www.googleapis.com/auth/calendar.events',
];
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function serviceError(code, message) {
  const error = new Error(message);
  error.code = code;
  return error;
}

function projectKey(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 64);
}

function emailAddress(value) {
  return String(value || '').trim().toLowerCase().slice(0, 254);
}

async function kvCmd(...args) {
  if (!process.env.KV_REST_API_URL || !process.env.KV_REST_API_TOKEN) throw serviceError('storage_unavailable', 'Calendar storage is unavailable.');
  const response = await fetch(process.env.KV_REST_API_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.KV_REST_API_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.error) throw serviceError('storage_unavailable', 'Calendar storage is unavailable.');
  return payload.result ?? null;
}

function encode(bytes) {
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function decode(value) {
  const binary = atob(String(value).replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(value.length / 4) * 4, '='));
  return Uint8Array.from(binary, character => character.charCodeAt(0));
}

async function encryptionKey() {
  if (!process.env.ADMIN_SECRET) throw serviceError('not_configured', 'Admin security is not configured.');
  const material = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`${process.env.ADMIN_SECRET}:google-calendar-v1`));
  return crypto.subtle.importKey('raw', material, 'AES-GCM', false, ['encrypt', 'decrypt']);
}

async function seal(value) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const cipher = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, await encryptionKey(), new TextEncoder().encode(JSON.stringify(value)));
  return `${encode(iv)}.${encode(new Uint8Array(cipher))}`;
}

async function unseal(value) {
  if (!value || !String(value).includes('.')) return null;
  try {
    const [iv, cipher] = String(value).split('.');
    const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: decode(iv) }, await encryptionKey(), decode(cipher));
    return JSON.parse(new TextDecoder().decode(plain));
  } catch {
    return null;
  }
}

export async function saveGoogleCalendarClient(projectId, input) {
  const id = projectKey(projectId);
  const clientId = String(input.clientId || '').trim().slice(0, 500);
  const clientSecret = String(input.clientSecret || '').trim().slice(0, 500);
  const expectedEmail = emailAddress(input.expectedEmail);
  if (!id || !clientId || !clientSecret || !EMAIL_PATTERN.test(expectedEmail)) {
    throw serviceError('invalid_client', 'Enter the Google account email, client ID, and client secret.');
  }
  const previous = await getClient(id);
  await kvCmd('HSET', CLIENT_KEY, id, await seal({ clientId, clientSecret, expectedEmail }));
  if (previous && (previous.clientId !== clientId || previous.clientSecret !== clientSecret || previous.expectedEmail !== expectedEmail)) {
    await kvCmd('HDEL', CONNECTION_KEY, id);
  }
  return { configured: true, expectedEmail };
}

async function getClient(projectId) {
  const stored = await unseal(await kvCmd('HGET', CLIENT_KEY, projectKey(projectId)));
  if (stored?.clientId && stored?.clientSecret && stored?.expectedEmail) return stored;
  const expectedEmail = emailAddress(process.env.GOOGLE_CALENDAR_EMAIL);
  if (process.env.GOOGLE_CALENDAR_CLIENT_ID && process.env.GOOGLE_CALENDAR_CLIENT_SECRET && EMAIL_PATTERN.test(expectedEmail)) {
    return { clientId: process.env.GOOGLE_CALENDAR_CLIENT_ID, clientSecret: process.env.GOOGLE_CALENDAR_CLIENT_SECRET, expectedEmail };
  }
  return null;
}

async function getConnection(projectId) {
  return unseal(await kvCmd('HGET', CONNECTION_KEY, projectKey(projectId)));
}

async function saveConnection(projectId, value) {
  await kvCmd('HSET', CONNECTION_KEY, projectKey(projectId), await seal(value));
}

export async function getGoogleCalendarStatus(projectId) {
  const [client, connection] = await Promise.all([getClient(projectId), getConnection(projectId)]);
  return {
    clientConfigured: Boolean(client),
    connected: Boolean(client && connection?.refreshToken && connection?.email === client.expectedEmail),
    email: connection?.email || '',
    expectedEmail: client?.expectedEmail || '',
    connectedAt: connection?.connectedAt || null,
  };
}

export async function createGoogleCalendarAuthorization(projectId, origin) {
  const id = projectKey(projectId);
  const client = await getClient(id);
  if (!client) throw serviceError('client_missing', 'Save the Google Calendar OAuth client first.');
  const redirectUri = new URL('/api/google-calendar/callback', origin).toString();
  const state = await seal({ projectId: id, redirectUri, expiresAt: Date.now() + 10 * 60 * 1000, nonce: crypto.randomUUID() });
  const query = new URLSearchParams({
    client_id: client.clientId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: SCOPES.join(' '),
    access_type: 'offline',
    prompt: 'consent',
    login_hint: client.expectedEmail,
    state,
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${query}`;
}

async function tokenRequest(client, fields) {
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ client_id: client.clientId, client_secret: client.clientSecret, ...fields }),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || !payload.access_token) throw serviceError('token_exchange', 'Google did not issue a calendar access token.');
  return payload;
}

export async function completeGoogleCalendarAuthorization(code, state) {
  const savedState = await unseal(state);
  if (!savedState?.projectId || !savedState?.redirectUri || Number(savedState.expiresAt) < Date.now()) {
    throw serviceError('invalid_state', 'The Google Calendar connection request expired.');
  }
  const client = await getClient(savedState.projectId);
  if (!client) throw serviceError('client_missing', 'The Google Calendar OAuth client is missing.');
  const tokens = await tokenRequest(client, {
    code: String(code || ''), grant_type: 'authorization_code', redirect_uri: savedState.redirectUri,
  });
  if (tokens.scope) {
    const granted = new Set(String(tokens.scope).split(/\s+/));
    if (!SCOPES.every(scope => granted.has(scope))) throw serviceError('calendar_access_failed', 'Grant both Google Calendar permissions to continue.');
  }
  const profileResponse = await fetch('https://openidconnect.googleapis.com/v1/userinfo', {
    headers: { Authorization: `Bearer ${tokens.access_token}` },
  });
  const profile = await profileResponse.json().catch(() => ({}));
  const email = emailAddress(profile.email);
  if (!profileResponse.ok || !profile.email_verified || email !== client.expectedEmail) {
    throw serviceError('account_mismatch', `Sign in with ${client.expectedEmail} to connect its calendar.`);
  }
  const checkedAt = new Date();
  const availabilityResponse = await fetch('https://www.googleapis.com/calendar/v3/freeBusy', {
    method: 'POST',
    headers: { Authorization: `Bearer ${tokens.access_token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ timeMin: checkedAt.toISOString(), timeMax: new Date(checkedAt.getTime() + 3600000).toISOString(), items: [{ id: 'primary' }] }),
  });
  const availability = await availabilityResponse.json().catch(() => ({}));
  if (!availabilityResponse.ok || availability.calendars?.primary?.errors?.length || !Array.isArray(availability.calendars?.primary?.busy)) {
    throw serviceError('calendar_access_failed', 'Enable Google Calendar API and grant calendar access before connecting.');
  }
  const previous = await getConnection(savedState.projectId);
  const refreshToken = tokens.refresh_token || (previous?.email === email ? previous.refreshToken : '');
  if (!refreshToken) throw serviceError('refresh_token_missing', 'Google did not provide offline calendar access.');
  await saveConnection(savedState.projectId, {
    email, accessToken: tokens.access_token, refreshToken,
    expiresAt: Date.now() + Math.max(300, Number(tokens.expires_in) || 3600) * 1000,
    connectedAt: previous?.connectedAt || Date.now(),
  });
  return { projectId: savedState.projectId, email };
}

async function validAccessToken(projectId, connection, client, force = false) {
  if (!force && connection.accessToken && Number(connection.expiresAt) > Date.now() + 120000) return connection;
  const tokens = await tokenRequest(client, { grant_type: 'refresh_token', refresh_token: connection.refreshToken });
  const updated = {
    ...connection, accessToken: tokens.access_token,
    expiresAt: Date.now() + Math.max(300, Number(tokens.expires_in) || 3600) * 1000,
  };
  await saveConnection(projectId, updated);
  return updated;
}

async function calendarRequest(projectId, path, init = {}) {
  const id = projectKey(projectId);
  const client = await getClient(id);
  let connection = await getConnection(id);
  if (!client || !connection?.refreshToken || connection.email !== client.expectedEmail) throw serviceError('calendar_not_connected', 'Connect Google Calendar in CRM Setup before booking a call.');
  connection = await validAccessToken(id, connection, client);
  const request = token => fetch(`https://www.googleapis.com/calendar/v3${path}`, {
    ...init,
    headers: { Accept: 'application/json', Authorization: `Bearer ${token}`, ...(init.body ? { 'Content-Type': 'application/json' } : {}) },
  });
  let response = await request(connection.accessToken);
  if (response.status === 401) {
    connection = await validAccessToken(id, connection, client, true);
    response = await request(connection.accessToken);
  }
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw serviceError('google_calendar_failed', payload.error?.message || 'Google Calendar is temporarily unavailable.');
  return payload;
}

export async function googleBusyIntervals(projectId, from, to) {
  const status = await getGoogleCalendarStatus(projectId);
  if (!status.connected) return null;
  const payload = await calendarRequest(projectId, '/freeBusy', {
    method: 'POST',
    body: JSON.stringify({ timeMin: new Date(from).toISOString(), timeMax: new Date(to).toISOString(), items: [{ id: 'primary' }] }),
  });
  const calendar = payload.calendars?.primary || payload.calendars?.[status.email];
  if (!calendar || calendar.errors?.length || !Array.isArray(calendar.busy)) throw serviceError('google_calendar_failed', 'Google Calendar availability could not be checked.');
  return calendar.busy.map(item => ({ start: new Date(item.start).getTime(), end: new Date(item.end).getTime() }))
    .filter(item => Number.isFinite(item.start) && Number.isFinite(item.end));
}

export async function createGoogleCalendarEvent(booking) {
  const id = booking.id.replace(/-/g, '').toLowerCase();
  const payload = await calendarRequest(booking.projectId, '/calendars/primary/events', {
    method: 'POST',
    body: JSON.stringify({
      id,
      summary: `Lofts Studio project call with ${booking.leadName}`,
      description: `Enquiry with ${booking.leadName} (${booking.leadEmail}). Phone: ${booking.phone}.\n\n${booking.note || booking.focus || 'Discuss the enquiry and next step.'}`,
      start: { dateTime: new Date(booking.startAt).toISOString(), timeZone: booking.hostTimezone },
      end: { dateTime: new Date(booking.endAt).toISOString(), timeZone: booking.hostTimezone },
      reminders: { useDefault: false, overrides: [{ method: 'popup', minutes: 15 }] },
      extendedProperties: { private: { loftsBookingId: booking.id } },
    }),
  });
  if (payload.id !== id) throw serviceError('google_calendar_failed', 'Google Calendar did not confirm the event.');
  return { id, htmlLink: payload.htmlLink || '' };
}

export async function deleteGoogleCalendarEvent(projectId, eventId) {
  await calendarRequest(projectId, `/calendars/primary/events/${encodeURIComponent(eventId)}`, { method: 'DELETE' });
}

export async function disconnectGoogleCalendar(projectId) {
  await kvCmd('HDEL', CONNECTION_KEY, projectKey(projectId));
}
