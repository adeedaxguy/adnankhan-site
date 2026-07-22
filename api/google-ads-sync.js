export const config = { runtime: 'edge' };

const ADMIN_SECRET = process.env.ADMIN_SECRET;
const KV_URL = process.env.KV_REST_API_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN;

async function kvCmd(...args) {
  if (!KV_URL || !KV_TOKEN) return null;
  const response = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  if (!response.ok) return null;
  const payload = await response.json();
  return payload.result ?? null;
}

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', 'Cache-Control': 'no-store' },
  });
}

async function syncToken(projectId) {
  if (!ADMIN_SECRET) return '';
  const input = new TextEncoder().encode(`${ADMIN_SECRET}:${projectId}:google-ads-sync-v1`);
  const digest = await crypto.subtle.digest('SHA-256', input);
  return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
}

function secureEqual(left, right) {
  if (!left || !right || left.length !== right.length) return false;
  let mismatch = 0;
  for (let index = 0; index < left.length; index += 1) mismatch |= left.charCodeAt(index) ^ right.charCodeAt(index);
  return mismatch === 0;
}

function number(value, maximum = 1e12) {
  return Math.min(maximum, Math.max(0, Number(value) || 0));
}

function text(value, limit = 160) {
  return String(value || '').slice(0, limit);
}

export default async function handler(req) {
  if (req.method !== 'POST') return jsonResponse({ error: 'Method not allowed.' }, 405);

  const body = await req.json().catch(() => ({}));
  const projectId = text(body.projectId, 64).toLowerCase().replace(/[^a-z0-9-]/g, '');
  const providedToken = req.headers.get('x-ads-sync-token') || '';
  const expectedToken = await syncToken(projectId);
  if (!projectId || !secureEqual(providedToken, expectedToken)) return jsonResponse({ error: 'Unauthorized.' }, 401);

  const now = Date.now();
  const accountId = text(body.accountId, 32);
  const campaigns = Array.isArray(body.campaigns) ? body.campaigns.slice(0, 50) : [];
  const keywords = Array.isArray(body.keywords) ? body.keywords.slice(0, 1000) : [];

  for (const item of campaigns) {
    const campaignId = text(item.id, 32).replace(/\D/g, '');
    if (!campaignId) continue;
    const snapshot = {
      campaignId,
      campaignName: text(item.name, 180),
      campaignStatus: text(item.status, 32),
      impressions: number(item.impressions),
      clicks: number(item.clicks),
      cost: number(item.cost),
      conversions: number(item.conversions),
      qualified: 0,
      revenue: number(item.conversionValue),
      source: 'google_ads_script',
      accountId,
      dateRange: 'LAST_30_DAYS',
      _ts: now,
    };
    const key = `agency:campaign-snapshots:${projectId}`;
    const saved = await kvCmd('LPUSH', key, JSON.stringify(snapshot));
    if (saved === null) return jsonResponse({ error: 'Reporting storage is unavailable.' }, 503);
    await kvCmd('LTRIM', key, '0', '179');
  }

  const keywordMetrics = keywords.map(item => ({
    campaignId: text(item.campaignId, 32).replace(/\D/g, ''),
    keyword: text(item.keyword, 200),
    matchType: text(item.matchType, 32),
    status: text(item.status, 32),
    impressions: number(item.impressions),
    clicks: number(item.clicks),
    cost: number(item.cost),
    conversions: number(item.conversions),
  })).filter(item => item.keyword);

  const keywordsSaved = await kvCmd('HSET', 'agency:google-ads-keywords', projectId, JSON.stringify(keywordMetrics));
  if (keywordsSaved === null) return jsonResponse({ error: 'Reporting storage is unavailable.' }, 503);

  const connection = {
    status: 'verified',
    source: 'google_ads_script',
    accountId,
    accountName: text(body.accountName, 120),
    currencyCode: text(body.currencyCode, 8),
    timezone: text(body.timezone, 80),
    campaignCount: campaigns.length,
    keywordCount: keywordMetrics.length,
    lastSyncedAt: now,
  };
  const connectionSaved = await kvCmd('HSET', 'agency:connections', projectId, JSON.stringify(connection));
  if (connectionSaved === null) return jsonResponse({ error: 'Reporting storage is unavailable.' }, 503);

  return jsonResponse({ ok: true, projectId, received: { campaigns: campaigns.length, keywords: keywordMetrics.length }, syncedAt: now });
}
