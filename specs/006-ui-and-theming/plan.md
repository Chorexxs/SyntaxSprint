# Plan técnico 006 — Sistema visual, temas y responsividad

| Campo | Valor |
| --- | --- |
| Spec | `specs/006-ui-and-theming/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Crear `templates/base.html` con el esqueleto común y refactorizar las cuatro plantillas
para que lo extiendan. Mantener Tailwind por CDN en esta fase y centralizar el script de
tema en un archivo estático (`static/js/theme.js`) cargado con `defer`. Corregir los
problemas de accesibilidad sin alterar la identidad visual.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `templates/base.html` | Crear | Head, header, footer, bloques `content` y `scripts`. |
| `templates/index.html` | Modificar | Extender `base.html`; conservar IDs del motor. |
| `templates/login.html` | Modificar | Extender `base.html`. |
| `templates/signup.html` | Modificar | Extender `base.html`. |
| `templates/profile.html` | Modificar | Extender `base.html`. |
| `static/js/theme.js` | Crear | Inicialización y toggle de tema. |
| `static/css/styles.css` | Modificar | Reemplazar `outline: none` por `:focus-visible`. |

## 3. Diseño de la plantilla base

```django
{% load static %}
<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
  ...
  <script>
    (function () {
      const saved = localStorage.getItem('theme');
      const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
      document.documentElement.setAttribute('data-theme', saved || (prefersLight ? 'light' : 'dark'));
    })();
  </script>
  {% block head %}{% endblock %}
</head>
<body>
  {% include "partials/header.html" %}
  {% block content %}{% endblock %}
  {% include "partials/footer.html" %}
  <script src="{% static 'js/theme.js' %}" defer></script>
  {% block scripts %}{% endblock %}
</body>
</html>
```

## 4. Accesibilidad

| Elemento | Cambio |
| --- | --- |
| Toggle de tema | `aria-label="Toggle theme"`, `aria-pressed` dinámico. |
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

1. Crear `base.html` y partials.
2. Migrar `index.html` y validar motor.
3. Migrar login, signup y profile.
4. Extraer `theme.js` y eliminar duplicados.
5. Corregir foco, labels y `aria`.
6. Revisar responsive y contraste.

## 9. Notas de despliegue

- Sin migraciones.
- Invalidar caché de CSS/JS tras el refactor.
