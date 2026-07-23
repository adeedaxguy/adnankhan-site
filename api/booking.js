import { createBooking, getAvailableSlots } from './_lib/automation.js';

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
    try {
      return json(await getAvailableSlots(url.searchParams.get('t')));
    } catch (error) {
      const status = error.code === 'invalid_token' || error.code === 'not_found' ? 404 : 400;
      return json({ error: error.message || 'Booking is unavailable.' }, status);
    }
  }
  if (req.method !== 'POST') return json({ error: 'Method not allowed' }, 405);
  const body = await req.json().catch(() => ({}));
  try {
    return json({ ok: true, ...await createBooking(body.token, body) }, 201);
  } catch (error) {
    const status = error.code === 'slot_unavailable' ? 409 : error.code === 'invalid_token' ? 404 : 400;
    return json({ ok: false, error: error.message || 'The call could not be booked.' }, status);
  }
}
