# Plan técnico 006 — Sistema visual, temas y responsividad

| Campo | Valor |
| --- | --- |
| Spec | `specs/006-ui-and-theming/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Crear `templates/base.html` con el esqueleto común y refactorizar las cuatro plantillas
para que lo extiendan. Mantener Tailwind por CDN en esa fase (sustituido por un build
local el 2026-11-11) y centralizar el script de tema en un archivo estático
(`static/js/theme.js`) cargado con `defer`. El header y el footer viven directamente en
`base.html`: solo se usan ahí y los partials añadirían indirección sin beneficio
(Artículo 2 de la constitución).

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `templates/base.html` | Crear | Head, header, footer, bloques `content`, `main_class` y `scripts`. |
| `templates/index.html` | Modificar | Extender `base.html`; conservar IDs del motor. |
| `templates/login.html` | Modificar | Extender `base.html`. |
| `templates/signup.html` | Modificar | Extender `base.html`. |
| `templates/profile.html` | Modificar | Extender `base.html`. |
| `static/js/theme.js` | Crear | Inicialización y toggle de tema. |
| `static/js/script.js` | Modificar | Quitar el tema: ahora es responsabilidad de `theme.js`. |
| `static/css/styles.css` | Modificar | Reemplazar `outline: none` por `:focus-visible`. |

## 3. Diseño de la plantilla base

```django
{% load static %}
<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
  ...
  {# Antes del primer pintado; evita FOUC (RNF-006-01). #}
  <script>
    (function () {
      try {
        const saved = localStorage.getItem('theme');
        document.documentElement.setAttribute(
          'data-theme', saved === 'light' ? 'light' : 'dark'
        );
      } catch (error) {
        document.documentElement.setAttribute('data-theme', 'dark');
      }
    })();
  </script>
  <script src="{% static 'js/theme.js' %}" defer></script>
  {% block extra_head %}{% endblock %}
</head>
<body>
  <header>...</header>
  <main class="{% block main_class %}...{% endblock %}">
    {% block content %}{% endblock %}
  </main>
  <footer>...</footer>
  {% block scripts %}{% endblock %}
</body>
</html>
```

> `prefers-color-scheme` (RF-006-09) no se aplica todavía: se mantiene el tema oscuro por
> defecto de RF-006-01 y queda para `T006-15`.

## 4. Accesibilidad

| Elemento | Cambio |
| --- | --- |
| Toggle de tema | `aria-label` en español y `aria-pressed` dinámico. |
| Inputs de login/signup | `<label class="sr-only">` o `aria-label`. |
| Mensajes | `role="alert"`. |
| Foco | `:focus-visible { outline: 2px solid var(--caret); outline-offset: 2px; }`. |
| Tabla de perfil | `scope="col"` en `th`. |
| Textarea oculto | `aria-label="Typing input"`, sin `tabindex=-1`. |

## 5. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| `base.html` + partials | DRY, cambios centralizados | Requiere tocar 4 plantillas | Sí |
| Web component de header | Encapsulación | Complejidad innecesaria | No |
| Tailwind compilado local | Producción correcta | Añade build | 007 |
| Dark-only | Simple | Pierde preferencia del usuario | No |

## 6. Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
| --- | --- | --- |
| Manual | Tema persiste entre páginas y recargas | Navegador |
| Manual | 320 / 768 / 1440 px sin overflow | DevTools |
| Manual | Navegación completa con Tab | Teclado |
| Automático | Contraste de tokens | Lighthouse / axe |
| Regresión | Las 4 páginas renderizan 200 | `TestCase` |

Checklist:

- [ ] Tema oscuro por defecto en ventana privada.
- [ ] Cambiar a claro y navegar a perfil mantiene el tema.
- [ ] Sin parpadeo al recargar.
- [ ] Foco visible en todos los controles.
- [ ] Sin scroll horizontal a 320 px.
- [ ] Lighthouse Accessibility ≥ 95.

## 7. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| Refactor rompe IDs del motor | Media | Mantener IDs y correr checklist de 004 |
| `base.html` cambia el contexto de mensajes | Baja | Incluir bloque de mensajes global |
| Script inline bloqueado por CSP futura | Media | Documentar nonce/hash al añadir CSP en 007 |

## 8. Orden de implementación

1. Crear `base.html` (header y footer incluidos).
2. Migrar `index.html` y validar motor.
3. Migrar login, signup y profile.
4. Extraer `theme.js` y eliminar duplicados.
5. Corregir foco, labels y `aria`.
6. Revisar responsive y contraste.

## 9. Notas de despliegue

- Sin migraciones.
- Invalidar caché de CSS/JS tras el refactor.

## 10. Decisiones posteriores (2026-11-11)

### T006-12 — Tokens ajustados por contraste

La medición inicial con la fórmula WCAG daba ratios muy por debajo de AA:

| Par | Antes | Después |
| --- | ---: | ---: |
| Oscuro `--text-sub` sobre `--bg-primary` | 2.17:1 | 4.54:1 |
| Oscuro `--text-sub` sobre `--bg-secondary` | 2.28:1 | 4.77:1 |
| Claro `--text-sub` sobre `--bg-primary` | 2.40:1 | 5.69:1 |
| Claro `--text-sub` sobre `--bg-secondary` | 2.13:1 | 5.06:1 |
| Oscuro `--error` sobre `--bg-primary` | 2.70:1 | 4.98:1 |
| Claro `--error` sobre `--bg-primary` | 3.69:1 | 4.99:1 |
| Claro `--success` sobre `--bg-primary` | 2.78:1 | 4.70:1 |

Se ajustaron también `--error` y `--success` porque se usan en texto de 14 px
(mensajes de login/signup y prompt en móvil), donde AA exige 4.5:1. `--text-main` y
`--success` en oscuro ya cumplían.

Decisiones asociadas:

- El footer pierde la opacidad `/60`: el texto atenuado incumplía AA.
- `::placeholder` usa `--text-sub` con `opacity: 1` para no heredar el gris por defecto
  del navegador.
- `#language-select` recibe un `<label class="sr-only">`; axe lo marcaba como
  `select-name` crítico aunque T006-10 solo cubría login y signup.

### T006-13/14/15 — Verificación y preferencia del sistema

Con Tailwind compilado (2026-11-11) se completó la verificación:

- Responsive: 320/768/1440 px en las 4 páginas sin scroll horizontal ni elementos fuera
  del viewport.
- Tema claro/oscuro persistente entre páginas y recarga; la preferencia guardada gana
  sobre la del sistema.
- `theme-init.js`: preferencia guardada > `prefers-color-scheme` > oscuro.
- Lighthouse (desktop): Accessibility 100, Best Practices 100, SEO 100.

La limitación anterior de `axe-core` (CDN de Tailwind inalcanzable) desapareció al
compilar Tailwind localmente; los ratios se calcularon con la fórmula de WCAG 2.1.

