import { completeZohoAuthorization } from '../_lib/zoho.js';

export const config = { runtime: 'edge' };

function redirect(origin, params) {
  const url = new URL('/admin/agency.html', origin);
  for (const [key, value] of Object.entries(params)) url.searchParams.set(key, value);
  return new Response(null, { status: 302, headers: { Location: url.toString(), 'Cache-Control': 'no-store' } });
}

export default async function handler(req) {
  const url = new URL(req.url);
  const error = url.searchParams.get('error');
  if (error) return redirect(url.origin, { zoho: 'error', reason: 'access_denied' });
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');
  if (!code || !state) return redirect(url.origin, { zoho: 'error', reason: 'missing_response' });
  try {
    const connection = await completeZohoAuthorization(code, state);
    return redirect(url.origin, { zoho: 'connected', project: connection.projectId });
  } catch (connectionError) {
    const reason = String(connectionError?.code || 'connection_failed').replace(/[^a-z0-9_-]/g, '').slice(0, 48);
    return redirect(url.origin, { zoho: 'error', reason });
  }
}
