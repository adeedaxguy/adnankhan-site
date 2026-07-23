import { recordEmailEngagement } from '../_lib/automation.js';

export const config = { runtime: 'edge' };

const GIF = Uint8Array.from(atob('R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs='), character => character.charCodeAt(0));

export default async function handler(req) {
  const token = new URL(req.url).searchParams.get('t');
  try {
    await recordEmailEngagement(token, 'open', { userAgent: req.headers.get('user-agent') || '' });
  } catch { /* Tracking must never break the email image response. */ }
  return new Response(GIF, {
    headers: {
      'content-type': 'image/gif',
      'content-length': String(GIF.byteLength),
      'Cache-Control': 'no-store, max-age=0',
    },
  });
}
