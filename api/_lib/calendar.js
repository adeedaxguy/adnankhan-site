import { getZohoStatus, sendZohoEmail, zohoCalendarRequest } from './zoho.js';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[character]);
}

function emailFrame(content) {
  return `<!doctype html><html lang="en"><body style="margin:0;padding:0;background:#f4f0e9">
    <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background:#f4f0e9"><tr><td align="center" style="padding:24px 10px">
      <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;background:#fbfaf7;border-top:3px solid #a9432d">
        <tr><td style="padding:27px 30px 17px;color:#171411;font-family:Georgia,serif;font-size:26px;line-height:1.2">Lofts Studio<span style="color:#a9432d">.</span></td></tr>
        <tr><td style="padding:10px 30px 30px;color:#171411;font-family:Arial,sans-serif;font-size:15px;line-height:1.65">${content}</td></tr>
        <tr><td style="padding:17px 30px;background:#ebe5db;color:#4f4942;font-family:Arial,sans-serif;font-size:12px;line-height:1.6">Lofts Studio &nbsp; | &nbsp; <a href="https://lofts.studio" style="color:#843322">lofts.studio</a> &nbsp; | &nbsp; <a href="mailto:hi@lofts.studio" style="color:#843322">hi@lofts.studio</a></td></tr>
      </table>
    </td></tr></table></body></html>`;
}

function detailRows(rows) {
  return `<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin:20px 0 23px;border-top:1px solid #d7cec2">${rows.map(([label, value]) => `
    <tr><td style="padding:12px 12px 12px 0;border-bottom:1px solid #e6ded4;color:#766f67;font-family:Arial,sans-serif;font-size:12px;vertical-align:top;width:120px">${escapeHtml(label)}</td>
    <td style="padding:12px 0;border-bottom:1px solid #e6ded4;color:#171411;font-family:Arial,sans-serif;font-size:15px;line-height:1.5;overflow-wrap:anywhere">${escapeHtml(value)}</td></tr>`).join('')}</table>`;
}

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

export async function notifyBooking(booking, config = {}) {
  const recipients = bookingNotifyEmails(config);
  if (!recipients.length) return false;
  const date = new Intl.DateTimeFormat('en-US', { timeZone: booking.hostTimezone, dateStyle: 'full', timeStyle: 'short' }).format(new Date(booking.startAt));
  const leadTimezone = booking.bookingTimezone || booking.hostTimezone;
  const leadDate = new Intl.DateTimeFormat('en-US', { timeZone: leadTimezone, dateStyle: 'full', timeStyle: 'short' }).format(new Date(booking.startAt));
  const subject = `${booking.status === 'confirmed' ? 'Call booked' : 'Call requested'}: ${booking.leadName}`;
  const calendarSummary = booking.calendarStatus === 'invited'
    ? 'Google invitations sent to the client and hi@lofts.studio'
    : 'Calendar needs review';
  const lines = [
    subject,
    `When: ${date} (${booking.hostTimezone})`,
    `Lead time: ${leadDate} (${leadTimezone})`,
    `Email: ${booking.leadEmail}`,
    `Phone: ${booking.phone || 'Not supplied'}`,
    `Enquiry: ${booking.focus || booking.note || 'See the CRM inbox'}`,
    `Calendar: ${calendarSummary}`,
    booking.meetUrl ? `Google Meet: ${booking.meetUrl}` : '',
    booking.googleCalendarUrl ? `Google Calendar: ${booking.googleCalendarUrl}` : '',
  ];
  const html = emailFrame(`<h1 style="margin:0 0 15px;font-family:Georgia,serif;font-size:27px;font-weight:400;line-height:1.25">${booking.status === 'confirmed' ? 'A call is booked.' : 'A call was requested.'}</h1>
    <p style="margin:0 0 20px;color:#4f4942">${escapeHtml(booking.leadName)} selected a time for a Lofts Studio project conversation.</p>
    ${detailRows([['Your time', `${date} (${booking.hostTimezone})`], ['Client time', `${leadDate} (${leadTimezone})`], ['Email', booking.leadEmail], ['Phone', booking.phone || 'Not supplied'], ['Enquiry', booking.focus || booking.note || 'See the CRM inbox'], ['Calendar', calendarSummary]])}
    ${booking.meetUrl ? `<p style="margin:0 0 15px"><a href="${escapeHtml(booking.meetUrl)}" style="color:#843322;font-weight:700">Open Google Meet</a></p>` : ''}
    ${booking.googleCalendarUrl ? `<p style="margin:0"><a href="${escapeHtml(booking.googleCalendarUrl)}" style="color:#843322">Open calendar event</a></p>` : ''}`);
  let delivered = true;
  for (const toAddress of recipients) {
    try {
      await sendZohoEmail(booking.projectId, { toAddress, subject, content: lines.filter(Boolean).join('\n'), htmlContent: html });
    } catch {
      if (!process.env.RESEND_API_KEY || booking.projectId !== 'lofts-studio') {
        delivered = false;
        continue;
      }
      try {
        const backup = await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            from: 'Lofts Studio <noreply@lofts.studio>',
            to: [toAddress],
            subject,
            text: lines.filter(Boolean).join('\n'),
            html,
            reply_to: 'hi@lofts.studio',
          }),
        });
        if (!backup.ok) delivered = false;
      } catch {
        delivered = false;
      }
    }
  }
  return delivered;
}

export async function confirmBookingToLead(booking, config = {}) {
  const timezone = booking.bookingTimezone || booking.hostTimezone;
  const date = new Intl.DateTimeFormat('en-US', { timeZone: timezone, dateStyle: 'full', timeStyle: 'short' }).format(new Date(booking.startAt));
  const confirmed = booking.status === 'confirmed';
  const subject = confirmed ? 'Your Lofts Studio call is confirmed' : 'Your Lofts Studio call request';
  const firstName = booking.leadName.split(/\s+/)[0] || 'there';
  const text = [
    `Hi ${firstName},`,
    '',
    confirmed ? `Your call with Lofts Studio is confirmed for ${date} (${timezone}).` : `We received your request for ${date} (${timezone}) and will confirm it shortly.`,
    `${booking.durationMinutes} minutes${booking.meetUrl ? ' on Google Meet' : ''}.`,
    booking.meetUrl ? `Join the call: ${booking.meetUrl}` : '',
    '',
    confirmed ? 'A Google Calendar invitation is also on its way. We will use the time to discuss your enquiry and the clearest next step. Reply here if anything changes.' : 'Reply here if you need to change your requested time.',
    '',
    config.senderName || 'Adnan Khan',
    config.senderRole || 'Founder, Lofts Studio',
  ].filter(line => line !== null).join('\n');
  const html = emailFrame(`<h1 style="margin:0 0 17px;font-family:Georgia,serif;font-size:27px;font-weight:400;line-height:1.25">${confirmed ? 'Your call is confirmed.' : 'Your time request is in.'}</h1>
    <p style="margin:0 0 14px">Hi ${escapeHtml(firstName)},</p>
    <p style="margin:0 0 14px">${confirmed ? 'We have set aside time to discuss your enquiry and the clearest next step.' : 'We received your preferred time and will confirm it shortly.'}</p>
    ${detailRows([['Date and time', `${date} (${timezone})`], ['Duration', `${booking.durationMinutes} minutes`], ['Format', booking.meetUrl ? 'Google Meet' : 'Video or phone']])}
    ${booking.meetUrl ? `<table role="presentation" cellpadding="0" cellspacing="0" style="margin:4px 0 22px"><tr><td bgcolor="#171411" style="background:#171411"><a href="${escapeHtml(booking.meetUrl)}" style="display:inline-block;padding:14px 21px;color:#fbfaf7;font-family:Arial,sans-serif;font-size:14px;font-weight:700;text-decoration:none">Join Google Meet</a></td></tr></table>
      <p style="margin:0 0 21px;color:#4f4942;font-size:13px">Meeting link: <a href="${escapeHtml(booking.meetUrl)}" style="color:#843322;overflow-wrap:anywhere">${escapeHtml(booking.meetUrl)}</a></p>` : ''}
    <p style="margin:0 0 20px;color:#4f4942">${confirmed ? 'A Google Calendar invitation is on its way as well. To change anything, simply reply to this email.' : 'To change your preferred time, simply reply to this email.'}</p>
    <p style="margin:0;padding-top:18px;border-top:1px solid #d7cec2"><strong>${escapeHtml(config.senderName || 'Adnan Khan')}</strong><br><span style="color:#4f4942;font-size:13px">${escapeHtml(config.senderRole || 'Founder, Lofts Studio')}</span></p>`);
  await sendZohoEmail(booking.projectId, { toAddress: booking.leadEmail, subject, content: text, htmlContent: html });
  return true;
}
