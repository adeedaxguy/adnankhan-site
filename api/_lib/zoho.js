const ADMIN_SECRET = process.env.ADMIN_SECRET;
const KV_URL = process.env.KV_REST_API_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN;

const CLIENT_KEY = 'agency:zoho-clients';
const CONNECTION_KEY = 'agency:zoho-mail';
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const DATA_CENTERS = {
  us: { accounts: 'https://accounts.zoho.com', mail: 'https://mail.zoho.com' },
  eu: { accounts: 'https://accounts.zoho.eu', mail: 'https://mail.zoho.eu' },
  in: { accounts: 'https://accounts.zoho.in', mail: 'https://mail.zoho.in' },
  au: { accounts: 'https://accounts.zoho.com.au', mail: 'https://mail.zoho.com.au' },
  jp: { accounts: 'https://accounts.zoho.jp', mail: 'https://mail.zoho.jp' },
  ca: { accounts: 'https://accounts.zohocloud.ca', mail: 'https://mail.zohocloud.ca' },
};

function serviceError(code, message) {
  const error = new Error(message);
  error.code = code;
  return error;
}

async function kvCmd(...args) {
  if (!KV_URL || !KV_TOKEN) throw serviceError('storage_unavailable', 'Agency storage is unavailable.');
  const response = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  if (!response.ok) throw serviceError('storage_unavailable', 'Agency storage is unavailable.');
  const payload = await response.json().catch(() => ({}));
  return payload.result ?? null;
}

function bytesToBase64Url(bytes) {
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function base64UrlToBytes(value) {
  const padded = String(value).replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(value.length / 4) * 4, '=');
  const binary = atob(padded);
  return Uint8Array.from(binary, character => character.charCodeAt(0));
}

async function encryptionKey() {
  if (!ADMIN_SECRET) throw serviceError('not_configured', 'Admin security is not configured.');
  const material = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`${ADMIN_SECRET}:zoho-mail-v1`));
  return crypto.subtle.importKey('raw', material, 'AES-GCM', false, ['encrypt', 'decrypt']);
}

async function seal(value) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const plaintext = new TextEncoder().encode(JSON.stringify(value));
  const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, await encryptionKey(), plaintext);
  return `${bytesToBase64Url(iv)}.${bytesToBase64Url(new Uint8Array(encrypted))}`;
}

async function unseal(value) {
  if (!value || !String(value).includes('.')) return null;
  try {
    const [iv, encrypted] = String(value).split('.');
    const plaintext = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: base64UrlToBytes(iv) },
      await encryptionKey(),
      base64UrlToBytes(encrypted),
    );
    return JSON.parse(new TextDecoder().decode(plaintext));
  } catch {
    return null;
  }
}

function cleanProjectId(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 64);
}

function cleanEmail(value) {
  return String(value || '').trim().toLowerCase().slice(0, 254);
}

function dataCenter(value) {
  return DATA_CENTERS[value] ? value : 'us';
}

export async function saveZohoClient(projectId, input) {
  const id = cleanProjectId(projectId);
  const clientId = String(input.clientId || '').trim().slice(0, 500);
  const clientSecret = String(input.clientSecret || '').trim().slice(0, 500);
  const fromEmail = cleanEmail(input.fromEmail);
  const dc = dataCenter(input.dataCenter);
  if (!id || !clientId || !clientSecret || !EMAIL_PATTERN.test(fromEmail)) {
    throw serviceError('invalid_client', 'Enter the sender email, client ID, and client secret.');
  }
  await kvCmd('HSET', CLIENT_KEY, id, await seal({ clientId, clientSecret, fromEmail, dataCenter: dc, updatedAt: Date.now() }));
  return { configured: true, fromEmail, dataCenter: dc };
}

export async function getZohoClient(projectId) {
  const id = cleanProjectId(projectId);
  const stored = await unseal(await kvCmd('HGET', CLIENT_KEY, id));
  if (stored?.clientId && stored?.clientSecret && stored?.fromEmail) return stored;
  const fromEmail = cleanEmail(process.env.ZOHO_FROM_EMAIL || process.env.CONTACT_EMAIL);
  if (process.env.ZOHO_CLIENT_ID && process.env.ZOHO_CLIENT_SECRET && EMAIL_PATTERN.test(fromEmail)) {
    return {
      clientId: process.env.ZOHO_CLIENT_ID,
      clientSecret: process.env.ZOHO_CLIENT_SECRET,
      fromEmail,
      dataCenter: dataCenter(process.env.ZOHO_DATA_CENTER),
    };
  }
  return null;
}

export async function getZohoConnection(projectId) {
  return unseal(await kvCmd('HGET', CONNECTION_KEY, cleanProjectId(projectId)));
}

async function saveZohoConnection(projectId, connection) {
  await kvCmd('HSET', CONNECTION_KEY, cleanProjectId(projectId), await seal(connection));
}

export async function getZohoStatus(projectId) {
  const [client, connection] = await Promise.all([getZohoClient(projectId), getZohoConnection(projectId)]);
  return {
    clientConfigured: Boolean(client),
    connected: Boolean(connection?.refreshToken && connection?.accountId),
    provider: connection?.provider || 'Zoho Mail',
    fromEmail: connection?.fromEmail || client?.fromEmail || '',
    accountId: connection?.accountId || '',
    connectedAt: connection?.connectedAt || null,
    lastSentAt: connection?.lastSentAt || null,
    dataCenter: connection?.dataCenter || client?.dataCenter || 'us',
    permission: 'Send only',
  };
}

export async function createZohoAuthorization(projectId, origin) {
  const id = cleanProjectId(projectId);
  const client = await getZohoClient(id);
  if (!client) throw serviceError('client_missing', 'Save the Zoho OAuth client first.');
  const dc = DATA_CENTERS[dataCenter(client.dataCenter)];
  const redirectUri = new URL('/api/zoho/callback', origin).toString();
  const state = await seal({ projectId: id, redirectUri, expiresAt: Date.now() + 10 * 60 * 1000, nonce: crypto.randomUUID() });
  const query = new URLSearchParams({
    scope: 'ZohoMail.messages.CREATE,ZohoMail.accounts.READ',
    client_id: client.clientId,
    response_type: 'code',
    access_type: 'offline',
    redirect_uri: redirectUri,
    prompt: 'consent',
    state,
  });
  return `${dc.accounts}/oauth/v2/auth?${query}`;
}

async function tokenRequest(client, fields) {
  const dc = DATA_CENTERS[dataCenter(client.dataCenter)];
  const response = await fetch(`${dc.accounts}/oauth/v2/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ client_id: client.clientId, client_secret: client.clientSecret, ...fields }),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.error || !payload.access_token) {
    throw serviceError('token_exchange', 'Zoho did not issue an access token.');
  }
  return payload;
}

function accountAddresses(account) {
  return [
    account.primaryEmailAddress,
    account.mailboxAddress,
    ...(Array.isArray(account.emailAddress) ? account.emailAddress.map(item => item.mailId) : []),
    ...(Array.isArray(account.sendMailDetails) ? account.sendMailDetails.map(item => item.fromAddress) : []),
  ].map(cleanEmail).filter(Boolean);
}

export async function completeZohoAuthorization(code, state) {
  const stateData = await unseal(state);
  if (!stateData?.projectId || !stateData?.redirectUri || Number(stateData.expiresAt) < Date.now()) {
    throw serviceError('invalid_state', 'The Zoho connection request expired.');
  }
  const projectId = cleanProjectId(stateData.projectId);
  const client = await getZohoClient(projectId);
  if (!client) throw serviceError('client_missing', 'The Zoho OAuth client is missing.');
  const tokens = await tokenRequest(client, {
    grant_type: 'authorization_code',
    code: String(code || ''),
    redirect_uri: stateData.redirectUri,
  });
  const dcName = dataCenter(client.dataCenter);
  const dc = DATA_CENTERS[dcName];
  const accountsResponse = await fetch(`${dc.mail}/api/accounts`, {
    headers: { Accept: 'application/json', Authorization: `Zoho-oauthtoken ${tokens.access_token}` },
  });
  const accountsPayload = await accountsResponse.json().catch(() => ({}));
  const accounts = Array.isArray(accountsPayload.data) ? accountsPayload.data : [];
  const fromEmail = cleanEmail(client.fromEmail);
  const account = accounts.find(item => accountAddresses(item).includes(fromEmail));
  if (!accountsResponse.ok || !account?.accountId) {
    throw serviceError('mailbox_not_found', 'The sender mailbox was not found in this Zoho account.');
  }
  const previous = await getZohoConnection(projectId);
  const refreshToken = tokens.refresh_token || previous?.refreshToken;
  if (!refreshToken) throw serviceError('refresh_token_missing', 'Zoho did not issue an offline refresh token.');
  await saveZohoConnection(projectId, {
    provider: 'Zoho Mail',
    fromEmail,
    accountId: String(account.accountId),
    accessToken: tokens.access_token,
    refreshToken,
    expiresAt: Date.now() + Math.max(300, Number(tokens.expires_in || tokens.expires_in_sec) || 3600) * 1000,
    connectedAt: previous?.connectedAt || Date.now(),
    lastSentAt: previous?.lastSentAt || null,
    dataCenter: dcName,
  });
  return { projectId, fromEmail };
}

async function validAccessToken(projectId, connection, client, force = false) {
  if (!force && connection.accessToken && Number(connection.expiresAt) > Date.now() + 2 * 60 * 1000) return connection;
  const tokens = await tokenRequest(client, { grant_type: 'refresh_token', refresh_token: connection.refreshToken });
  const updated = {
    ...connection,
    accessToken: tokens.access_token,
    expiresAt: Date.now() + Math.max(300, Number(tokens.expires_in || tokens.expires_in_sec) || 3600) * 1000,
  };
  await saveZohoConnection(projectId, updated);
  return updated;
}

async function postMessage(connection, toAddress, subject, content) {
  const dc = DATA_CENTERS[dataCenter(connection.dataCenter)];
  return fetch(`${dc.mail}/api/accounts/${encodeURIComponent(connection.accountId)}/messages`, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      Authorization: `Zoho-oauthtoken ${connection.accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      fromAddress: connection.fromEmail,
      toAddress,
      subject,
      content,
      mailFormat: 'plaintext',
      encoding: 'UTF-8',
    }),
  });
}

export async function sendZohoEmail(projectId, message) {
  const id = cleanProjectId(projectId);
  const client = await getZohoClient(id);
  let connection = await getZohoConnection(id);
  if (!client || !connection?.refreshToken || !connection?.accountId) {
    throw serviceError('not_connected', 'Connect Zoho Mail before sending email.');
  }
  const toAddress = cleanEmail(message.toAddress);
  const subject = String(message.subject || '').trim().slice(0, 180);
  const content = String(message.content || '').trim().slice(0, 10000);
  if (!EMAIL_PATTERN.test(toAddress) || !subject || !content) {
    throw serviceError('invalid_message', 'Recipient, subject, and message are required.');
  }
  connection = await validAccessToken(id, connection, client);
  let response = await postMessage(connection, toAddress, subject, content);
  if (response.status === 401) {
    connection = await validAccessToken(id, connection, client, true);
    response = await postMessage(connection, toAddress, subject, content);
  }
  const payload = await response.json().catch(() => ({}));
  const responseCode = Number(payload?.status?.code || response.status);
  if (!response.ok || responseCode >= 400) throw serviceError('send_failed', payload?.status?.description || 'Zoho could not send the email.');
  connection.lastSentAt = Date.now();
  await saveZohoConnection(id, connection);
  return {
    sentAt: connection.lastSentAt,
    fromEmail: connection.fromEmail,
    messageId: String(payload?.data?.messageId || payload?.data?.messageID || ''),
  };
}

export async function disconnectZoho(projectId) {
  await kvCmd('HDEL', CONNECTION_KEY, cleanProjectId(projectId));
}
