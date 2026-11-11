/**
 * Tema claro/oscuro de SyntaxSprint.
 *
 * El atributo `data-theme` inicial lo fija `theme-init.js` desde `base.html`
 * antes del primer pintado para evitar FOUC. Este archivo gestiona el botón,
 * los iconos y la persistencia en localStorage.
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'theme';
  const DEFAULT_THEME = 'dark';

  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') || DEFAULT_THEME;
  }

  function updateToggle(theme) {
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');
    const button = document.getElementById('theme-toggle');

    if (sunIcon && moonIcon) {
      sunIcon.classList.toggle('hidden', theme !== 'dark');
      moonIcon.classList.toggle('hidden', theme === 'dark');
    }

    if (button) {
      button.setAttribute('aria-pressed', theme === 'light' ? 'true' : 'false');
      button.setAttribute(
        'aria-label',
        theme === 'dark' ? 'Activar tema claro' : 'Activar tema oscuro'
      );
    }
  }

  function toggleTheme() {
    const nextTheme = currentTheme() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nextTheme);

    try {
      localStorage.setItem(STORAGE_KEY, nextTheme);
    } catch (error) {
      // Sin almacenamiento disponible: el tema dura solo esta página.
    }

    updateToggle(nextTheme);
  }

  function init() {
    updateToggle(currentTheme());

    const button = document.getElementById('theme-toggle');
    if (button) {
      button.addEventListener('click', toggleTheme);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
