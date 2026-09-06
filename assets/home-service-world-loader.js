(function () {
  'use strict';

  var world = document.querySelector('[data-home-service-world]');
  if (!world || !window.WebGLRenderingContext) return;

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var compact = window.matchMedia('(max-width: 980px), (pointer: coarse)').matches;
  var saveData = !!(navigator.connection && navigator.connection.saveData);
  var lowMemory = !!(navigator.deviceMemory && navigator.deviceMemory <= 4);
  if (reducedMotion || compact || saveData || lowMemory) {
    document.documentElement.classList.add('home-service-world-unavailable');
    return;
  }

  var canvas = document.createElement('canvas');
  var gl = null;
  try {
    gl = canvas.getContext('webgl2', { failIfMajorPerformanceCaveat: true }) ||
      canvas.getContext('webgl', { failIfMajorPerformanceCaveat: true });
  } catch (error) {
    gl = null;
  }
  if (!gl) {
    document.documentElement.classList.add('home-service-world-unavailable');
    return;
  }
  var loseContext = gl.getExtension('WEBGL_lose_context');
  if (loseContext) loseContext.loseContext();

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

  // Keep the useful first paint free of the 3D runtime. Desktop visitors start
  // the scene as soon as they interact; compact and reduced-motion clients keep
  // the fully rendered static service map.
}());
