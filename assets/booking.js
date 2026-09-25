const bookingToken = new URLSearchParams(window.location.search).get('t') || '';
const bookingState = {
  data: null,
  selected: '',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
  confirmed: null,
  dayKey: '',
  dayKeys: [],
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
  document.getElementById('booking-date-nav').hidden = true;
  document.getElementById('booking-days').hidden = true;
}

function dayKey(value) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: bookingState.timezone, year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(value));
}

function renderBookingSlots() {
  const container = document.getElementById('booking-days');
  const groups = new Map();
  for (const slot of bookingState.data.slots) {
    const key = dayKey(slot);
    const list = groups.get(key) || [];
    list.push(slot);
    groups.set(key, list);
  }
  bookingState.dayKeys = [...groups.keys()];
  if (groups.size && !groups.has(bookingState.dayKey)) bookingState.dayKey = bookingState.dayKeys[0];
  const dayIndex = bookingState.dayKeys.indexOf(bookingState.dayKey);
  const weekStart = Math.floor(Math.max(0, dayIndex) / 7) * 7;
  const weekDays = bookingState.dayKeys.slice(weekStart, weekStart + 7);
  const nav = document.getElementById('booking-date-nav');
  nav.hidden = !groups.size;
  if (groups.size) {
    document.getElementById('booking-week-label').textContent = `${formatSlot(groups.get(weekDays[0])[0], { month: 'short', day: 'numeric' })} - ${formatSlot(groups.get(weekDays.at(-1))[0], { month: 'short', day: 'numeric' })}`;
    document.getElementById('booking-prev-week').disabled = weekStart === 0;
    document.getElementById('booking-next-week').disabled = weekStart + 7 >= bookingState.dayKeys.length;
    const strip = document.getElementById('booking-date-strip');
    strip.innerHTML = weekDays.map(key => {
      const slot = groups.get(key)[0];
      return `<button type="button" data-day="${key}" class="${key === bookingState.dayKey ? 'selected' : ''}" aria-label="${formatSlot(slot, { weekday: 'long', month: 'long', day: 'numeric' })}" aria-pressed="${key === bookingState.dayKey}"><span>${formatSlot(slot, { weekday: 'short' })}</span><strong>${formatSlot(slot, { day: 'numeric' })}</strong></button>`;
    }).join('');
    strip.querySelectorAll('[data-day]').forEach(button => button.addEventListener('click', () => selectBookingDay(button.dataset.day)));
  }
  const slots = groups.get(bookingState.dayKey) || [];
  container.innerHTML = slots.length ? `<section class="booking-day"><div class="booking-day-label"><strong>${formatSlot(slots[0], { weekday: 'long' })}</strong><span>${formatSlot(slots[0], { month: 'long', day: 'numeric' })}</span></div><div class="booking-slot-grid">${slots.map(slot => `<button type="button" data-slot="${slot}" class="booking-slot ${slot === bookingState.selected ? 'selected' : ''}">${formatSlot(slot, { hour: 'numeric', minute: '2-digit' })}</button>`).join('')}</div></section>` : '<div class="booking-status error">No open times are available in the next few weeks. Email hi@lofts.studio and the team will arrange one manually.</div>';
  container.hidden = false;
  document.getElementById('booking-status').hidden = true;
  container.querySelectorAll('[data-slot]').forEach(button => button.addEventListener('click', () => selectBookingSlot(button.dataset.slot)));
  refreshBookingIcons();
}

function selectBookingDay(key) {
  bookingState.dayKey = key;
  bookingState.selected = '';
  document.getElementById('booking-form').hidden = true;
  renderBookingSlots();
}

function moveBookingWeek(direction) {
  const current = bookingState.dayKeys.indexOf(bookingState.dayKey);
  const next = Math.floor(Math.max(0, current) / 7) * 7 + direction * 7;
  if (next < 0 || next >= bookingState.dayKeys.length) return;
  selectBookingDay(bookingState.dayKeys[next]);
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

function showBookingConfirmation(booking, warning = '') {
  bookingState.confirmed = booking;
  document.getElementById('booking-status').hidden = true;
  document.getElementById('booking-days').hidden = true;
  document.getElementById('booking-form').hidden = true;
  const confirmed = document.getElementById('booking-confirmed');
  confirmed.hidden = false;
  document.getElementById('booking-date-nav').hidden = true;
  const requested = booking.status === 'requested';
  document.getElementById('booking-confirmed-kicker').textContent = requested ? 'Request received' : 'Confirmed';
  document.getElementById('booking-confirmed-title').textContent = requested ? 'Your time request is in.' : 'Your call is booked.';
  document.getElementById('booking-confirmed-note').textContent = warning || (requested
    ? 'We will confirm the time by email shortly. Reply there if anything changes.'
    : 'A confirmation has been sent to your email. Reply there if anything changes.');
  document.getElementById('booking-calendar').hidden = requested;
  document.getElementById('booking-confirmed-time').textContent = formatSlot(booking.startAt, {
    weekday: 'long', month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short',
  });
  refreshBookingIcons();
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
    showBookingConfirmation(result.booking, result.warning);
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
    if (data.booking) {
      showBookingConfirmation(data.booking);
      return;
    }
    bookingState.data = data;
    document.getElementById('booking-request-note').hidden = data.calendarConnected;
    document.getElementById('booking-submit-label').textContent = data.calendarConnected ? 'Confirm call' : 'Request this time';
    document.getElementById('booking-duration').textContent = `${data.durationMinutes} minutes`;
    document.getElementById('booking-name').value = data.lead.name || '';
    document.getElementById('booking-email').value = data.lead.email || '';
    document.getElementById('booking-phone').value = data.lead.phone || '';
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
  bookingState.dayKey = '';
  document.getElementById('booking-form').hidden = true;
  renderBookingSlots();
});
document.getElementById('booking-prev-week').addEventListener('click', () => moveBookingWeek(-1));
document.getElementById('booking-next-week').addEventListener('click', () => moveBookingWeek(1));
document.getElementById('booking-form').addEventListener('submit', submitBooking);
document.getElementById('booking-calendar').addEventListener('click', downloadCalendar);
refreshBookingIcons();
loadBooking();
