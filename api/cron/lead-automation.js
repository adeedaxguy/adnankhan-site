import { processDueAutomations } from '../_lib/automation.js';

export const config = { runtime: 'edge' };

export default async function handler(req) {
  const secret = process.env.CRON_SECRET || '';
  const authorization = req.headers.get('authorization') || '';
  if (!secret || authorization !== `Bearer ${secret}`) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'content-type': 'application/json' },
    });
  }
  try {
    const result = await processDueAutomations();
    return new Response(JSON.stringify({ ok: true, ...result }), {
      headers: { 'content-type': 'application/json', 'Cache-Control': 'no-store' },
    });
  } catch (error) {
    return new Response(JSON.stringify({ ok: false, error: error.message || 'Automation run failed.' }), {
      status: 500,
      headers: { 'content-type': 'application/json', 'Cache-Control': 'no-store' },
    });
  }
}
