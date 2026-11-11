/**
 * Aplica el tema guardado antes del primer pintado para evitar FOUC (RNF-006-01).
 *
 * Debe cargarse como script bloqueante en el `<head>`, antes del CSS.
 */
(function () {
  'use strict';

  try {
    const saved = localStorage.getItem('theme');
    document.documentElement.setAttribute(
      'data-theme', saved === 'light' ? 'light' : 'dark'
    );
  } catch (error) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
})();
