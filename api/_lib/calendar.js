import { getZohoStatus, sendZohoEmail, zohoCalendarRequest } from './zoho.js';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function basicUtc(value) {
  return new Date(value).toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
}

function parseBasicUtc(value) {
  const match = String(value || '').match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z?$/);
  return match ? Date.UTC(...[Number(match[1]), Number(match[2]) - 1, ...match.slice(3).map(Number)]) : NaN;
}

export function bookingNotifyEmails(config = {}) {
  const configured = config.bookingNotificationEmails || process.env.BOOKING_NOTIFY_EMAILS || [process.env.CONTACT_EMAIL, process.env.CONTACT_EMAIL_BCC].filter(Boolean).join(',');
  return [...new Set(configured.split(/[;,]/).map(value => value.trim().toLowerCase()).filter(value => EMAIL_PATTERN.test(value)))];
}

export async function busyCalendarIntervals(projectId, from, to) {
  const status = await getZohoStatus(projectId);
  if (!status.calendarConnected) return null;
  const payload = await zohoCalendarRequest(projectId, '/calendars/freebusy', {
    uemail: status.fromEmail,
    sdate: basicUtc(from).replace(/Z$/, ''),
    edate: basicUtc(to).replace(/Z$/, ''),
    ftype: 'eventbased',
  });
  if (!Array.isArray(payload.freebusy)) throw new Error('Calendar availability could not be checked.');
  return payload.freebusy.filter(item => item.fbtype === 'busy').map(item => ({
    start: parseBasicUtc(item.startTime),
    end: parseBasicUtc(item.endTime),
  })).filter(item => Number.isFinite(item.start) && Number.isFinite(item.end));
}

export async function createCalendarEvent(booking) {
  const status = await getZohoStatus(booking.projectId);
  if (!status.calendarConnected) return { status: 'not-connected' };
  const primary = await zohoCalendarRequest(booking.projectId, '/calendars/primary');
  const calendarUid = primary.calendars?.[0]?.uid;
  if (!calendarUid) throw new Error('The primary Zoho calendar could not be found.');
  const attendees = [booking.leadEmail]
    .filter(email => EMAIL_PATTERN.test(email) && email !== status.fromEmail)
    .map(email => ({ email, status: 'NEEDS-ACTION' }));
  const eventData = {
    title: `Lofts Studio project call with ${booking.leadName}`,
    dateandtime: { start: basicUtc(booking.startAt), end: basicUtc(booking.endAt), timezone: booking.hostTimezone },
    description: `Enquiry with ${booking.leadName} (${booking.leadEmail}). Phone: ${booking.phone || 'Not supplied'}.\n\n${booking.note || 'Discuss the enquiry and next step.'}`,
    attendees,
    notify_attendee: 1,
    reminders: [{ action: 'popup', minutes: -15 }],
    transparency: 0,
  };
  const created = await zohoCalendarRequest(booking.projectId, `/calendars/${encodeURIComponent(calendarUid)}/events`, { eventdata: JSON.stringify(eventData) }, 'POST');
  const event = created.events?.[0];
  if (!event?.uid) throw new Error('Zoho Calendar did not confirm the event.');
  return { status: 'created', uid: event.uid, calendarUid };
}

export async function notifyBooking(booking, config = {}) {
  const recipients = bookingNotifyEmails(config);
  if (!recipients.length) return false;
  const date = new Intl.DateTimeFormat('en-US', { timeZone: booking.hostTimezone, dateStyle: 'full', timeStyle: 'short' }).format(new Date(booking.startAt));
  const subject = `${booking.status === 'confirmed' ? 'Call booked' : 'Call requested'}: ${booking.leadName}`;
  const lines = [
    subject,
    `When: ${date} (${booking.hostTimezone})`,
    `Email: ${booking.leadEmail}`,
    `Phone: ${booking.phone || 'Not supplied'}`,
    `Enquiry: ${booking.focus || booking.note || 'See the CRM inbox'}`,
    `Calendar: ${booking.calendarStatus === 'created' ? 'Zoho and Google events created' : booking.calendarStatus === 'partial-google' ? 'Google event created; Zoho needs review' : booking.calendarStatus === 'zoho-review' ? 'Zoho outcome needs review; Google event rolled back' : 'Calendar connections needed'}`,
  ];
  let delivered = true;
  for (const toAddress of recipients) {
    try {
      await sendZohoEmail(booking.projectId, { toAddress, subject, content: lines.join('\n') });
    } catch {
      delivered = false;
    }
  }
  return delivered;
}

export async function confirmBookingToLead(booking, config = {}) {
  const date = new Intl.DateTimeFormat('en-US', { timeZone: booking.hostTimezone, dateStyle: 'full', timeStyle: 'short' }).format(new Date(booking.startAt));
  const confirmed = booking.status === 'confirmed';
  const subject = confirmed ? 'Your Lofts Studio call is confirmed' : 'Your Lofts Studio call request';
  const text = [
    `Hi ${booking.leadName.split(/\s+/)[0] || 'there'},`,
    '',
    confirmed ? `Your call with Lofts Studio is confirmed for ${date} (${booking.hostTimezone}).` : `We received your request for ${date} (${booking.hostTimezone}) and will confirm it shortly.`,
    '',
    'We will use the time to discuss your enquiry and the clearest next step. Reply here if anything changes.',
    '',
    config.senderName || 'Adnan Khan',
    config.senderRole || 'Founder, Lofts Studio',
  ].join('\n');
  await sendZohoEmail(booking.projectId, { toAddress: booking.leadEmail, subject, content: text });
  return true;
}
