import { unsubscribeLead, verifyAutomationToken } from './_lib/automation.js';

export const config = { runtime: 'edge' };

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', 'Cache-Control': 'no-store' },
  });
}

export default async function handler(req) {
  const url = new URL(req.url);
  if (req.method === 'GET') {
    const payload = await verifyAutomationToken(url.searchParams.get('t'), 'unsubscribe');
    if (!payload) return json({ valid: false, error: 'This unsubscribe link is invalid or expired.' }, 400);
    return json({ valid: true });
  }
  if (req.method !== 'POST') return json({ error: 'Method not allowed' }, 405);
  const body = await req.json().catch(() => ({}));
  try {
    const result = await unsubscribeLead(body.token);
    return json({ ok: true, unsubscribedAt: result.at });
  } catch (error) {
    return json({ ok: false, error: error.message || 'Could not stop follow-ups.' }, 400);
  }
}
