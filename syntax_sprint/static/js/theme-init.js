/**
 * Aplica el tema antes del primer pintado para evitar FOUC (RNF-006-01).
 *
 * Prioridad: preferencia guardada > `prefers-color-scheme` > oscuro (RF-006-09).
 * Debe cargarse como script bloqueante en el `<head>`, antes del CSS.
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'theme';
  const DEFAULT_THEME = 'dark';

  function preferredTheme() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'light' || saved === 'dark') {
        return saved;
      }
    } catch (error) {
      // Sin almacenamiento disponible: se usa la preferencia del sistema.
    }

    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return 'light';
    }
    return DEFAULT_THEME;
  }

  document.documentElement.setAttribute('data-theme', preferredTheme());
})();
