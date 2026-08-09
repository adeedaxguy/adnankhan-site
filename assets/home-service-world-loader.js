(function () {
  'use strict';

  var world = document.querySelector('[data-home-service-world]');
  if (!world || !window.WebGLRenderingContext) return;

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var compact = window.matchMedia('(max-width: 980px), (pointer: coarse)').matches;
  var saveData = !!(navigator.connection && navigator.connection.saveData);
  var lowMemory = !!(navigator.deviceMemory && navigator.deviceMemory <= 4);
  if (reducedMotion || compact || saveData || lowMemory) return;

  var started = false;
  var events = ['pointermove', 'pointerdown', 'keydown', 'scroll'];

  function start() {
    if (started) return;
    started = true;
    events.forEach(function (eventName) {
      window.removeEventListener(eventName, start);
    });
    import('/assets/home-service-world.js?v=20260809d').catch(function () {
      document.documentElement.classList.add('home-service-world-unavailable');
    });
  }

  events.forEach(function (eventName) {
    window.addEventListener(eventName, start, { once: true, passive: true });
  });
}());
