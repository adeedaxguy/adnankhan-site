const bookingToken = new URLSearchParams(window.location.search).get('t') || '';
const bookingState = {
  data: null,
  selected: '',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
  confirmed: null,
};

function refreshBookingIcons() {
  if (window.lucide) window.lucide.createIcons({ attrs: { 'aria-hidden': 'true' } });
}

function formatSlot(value, options = {}) {
  return new Intl.DateTimeFormat('en-US', { timeZone: bookingState.timezone, ...options }).format(new Date(value));
}

function timezoneOptions(hostTimezone) {
  return [...new Set([
    bookingState.timezone,
    hostTimezone,
    'America/New_York',
    'America/Los_Angeles',
    'Europe/London',
    'Asia/Dubai',
    'Asia/Karachi',
    'Australia/Sydney',
  ].filter(Boolean))];
}

function showBookingError(message) {
  const status = document.getElementById('booking-status');
  status.className = 'booking-status error';
  status.textContent = message;
  status.hidden = false;
  document.getElementById('booking-days').hidden = true;
}

function renderBookingSlots() {
  const container = document.getElementById('booking-days');
  const groups = new Map();
  for (const slot of bookingState.data.slots) {
    const key = formatSlot(slot, { year: 'numeric', month: '2-digit', day: '2-digit' });
    const list = groups.get(key) || [];
    list.push(slot);
    groups.set(key, list);
  }
  container.innerHTML = groups.size ? [...groups.values()].map(slots => {
    const first = slots[0];
    return `<section class="booking-day"><div class="booking-day-label"><strong>${formatSlot(first, { weekday: 'long' })}</strong><span>${formatSlot(first, { month: 'short', day: 'numeric' })}</span></div><div class="booking-slot-grid">${slots.map(slot => `<button type="button" data-slot="${slot}" class="booking-slot ${slot === bookingState.selected ? 'selected' : ''}">${formatSlot(slot, { hour: 'numeric', minute: '2-digit' })}</button>`).join('')}</div></section>`;
  }).join('') : '<div class="booking-status error">No open times are available in the next few weeks. Email hi@lofts.studio and the team will arrange one manually.</div>';
  container.hidden = false;
  document.getElementById('booking-status').hidden = true;
  container.querySelectorAll('[data-slot]').forEach(button => button.addEventListener('click', () => selectBookingSlot(button.dataset.slot)));
}

function selectBookingSlot(slot) {
  bookingState.selected = slot;
  renderBookingSlots();
  const form = document.getElementById('booking-form');
  form.hidden = false;
  document.getElementById('booking-selected').innerHTML = `<span><i data-lucide="calendar-days"></i>${formatSlot(slot, { weekday: 'long', month: 'long', day: 'numeric' })}</span><strong>${formatSlot(slot, { hour: 'numeric', minute: '2-digit', timeZoneName: 'short' })}</strong>`;
  refreshBookingIcons();
  form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function escapeIcs(value) {
  return String(value || '').replace(/\\/g, '\\\\').replace(/\n/g, '\\n').replace(/,/g, '\\,').replace(/;/g, '\\;');
}

function downloadCalendar() {
  const booking = bookingState.confirmed;
  if (!booking) return;
  const stamp = date => new Date(date).toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  const ics = [
    'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Lofts Studio//Booking//EN', 'CALSCALE:GREGORIAN',
    'BEGIN:VEVENT', `UID:${booking.id}@lofts.studio`, `DTSTAMP:${stamp(Date.now())}`,
    `DTSTART:${stamp(booking.startAt)}`, `DTEND:${stamp(booking.endAt)}`,
    'SUMMARY:Project call with Lofts Studio',
    `DESCRIPTION:${escapeIcs('Review the enquiry, current page, and clearest next step. Reply to hi@lofts.studio if anything changes.')}`,
    'END:VEVENT', 'END:VCALENDAR',
  ].join('\r\n');
  const link = document.createElement('a');
  link.href = URL.createObjectURL(new Blob([ics], { type: 'text/calendar;charset=utf-8' }));
  link.download = 'lofts-studio-call.ics';
  link.click();
  URL.revokeObjectURL(link.href);
}

async function submitBooking(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  document.getElementById('booking-error').textContent = '';
  try {
    const fields = Object.fromEntries(new FormData(form).entries());
    const response = await fetch('/api/booking', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ ...fields, token: bookingToken, start: bookingState.selected, timezone: bookingState.timezone }),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || 'The call could not be booked.');
    bookingState.confirmed = result.booking;
    document.getElementById('booking-days').hidden = true;
    form.hidden = true;
    const confirmed = document.getElementById('booking-confirmed');
    confirmed.hidden = false;
    document.getElementById('booking-confirmed-time').textContent = formatSlot(result.booking.startAt, {
      weekday: 'long', month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short',
    });
    refreshBookingIcons();
  } catch (error) {
    document.getElementById('booking-error').textContent = error.message;
    if (/no longer available|just booked/i.test(error.message)) await loadBooking();
  } finally {
    button.disabled = false;
  }
}

async function loadBooking() {
  if (!bookingToken) {
    showBookingError('This booking page needs the personal link from your Lofts Studio email. Email hi@lofts.studio if you need a new one.');
    return;
  }
  try {
    const response = await fetch(`/api/booking?t=${encodeURIComponent(bookingToken)}`, { headers: { Accept: 'application/json' } });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || 'Booking is unavailable.');
    bookingState.data = data;
    document.getElementById('booking-duration').textContent = `${data.durationMinutes} minutes`;
    document.getElementById('booking-name').value = data.lead.name || '';
    document.getElementById('booking-email').value = data.lead.email || '';
    const select = document.getElementById('booking-timezone');
    select.innerHTML = timezoneOptions(data.timezone).map(zone => `<option value="${zone}" ${zone === bookingState.timezone ? 'selected' : ''}>${zone.replace(/_/g, ' ')}</option>`).join('');
    renderBookingSlots();
    refreshBookingIcons();
  } catch (error) {
    showBookingError(error.message);
  }
}

document.getElementById('booking-timezone').addEventListener('change', event => {
  bookingState.timezone = event.target.value;
  bookingState.selected = '';
  document.getElementById('booking-form').hidden = true;
  renderBookingSlots();
});
document.getElementById('booking-form').addEventListener('submit', submitBooking);
document.getElementById('booking-calendar').addEventListener('click', downloadCalendar);
refreshBookingIcons();
loadBooking();
