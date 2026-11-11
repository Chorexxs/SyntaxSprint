# Spec 006 — Sistema visual, temas y responsividad

| Campo | Valor |
| --- | --- |
| Estado | Implementada |
| Versión | 1.0 |
| Depende de | 001-foundation |
| Archivos principales | `templates/*.html`, `static/css/styles.css`, `static/icon/icon.svg` |

## 1. Contexto y problema

La interfaz es minimalista, inspirada en MonkeyType: fondo oscuro, tipografía monoespaciada
y acentos sobrios. Cuatro plantillas duplican el header, el footer, la configuración de
Tailwind y el script de tema, lo que ya ha provocado inconsistencias y hace costoso
cualquier cambio visual.

## 2. Objetivos

1. Una identidad visual coherente en todas las páginas.
2. Tema claro/oscuro persistente y sin parpadeo.
3. Diseño responsive de 320 px a 1440 px.
4. Base de accesibilidad: foco visible, contraste AA y navegación por teclado.
5. Eliminar duplicación mediante una plantilla base.

### No objetivos

- Rediseño completo de marca.
- Animaciones complejas o transiciones de página.
- Modo de alto contraste dedicado.
- Cambio a un framework CSS con build (evaluar en 007).

## 3. Actores y casos de uso

| Actor | Caso de uso |
| --- | --- |
| Visitante | Navegar portada, login y signup con el tema recordado. |
| Usuario | Consultar perfil y volver al test manteniendo el tema. |
| Usuario de teclado | Navegar y usar controles sin ratón. |

## 4. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-006-01 | El sistema debe iniciar en tema oscuro cuando no hay preferencia guardada ni del sistema; si el SO prefiere claro, aplica `RF-006-09`. | Alta |
| RF-006-02 | Cuando el usuario pulsa el toggle, el sistema debe alternar el tema y guardarlo en `localStorage`. | Alta |
| RF-006-03 | Al cargar cualquier página, el sistema debe aplicar el tema guardado antes del primer pintado. | Alta |
| RF-006-04 | Todas las páginas deben compartir header, footer y tokens de color. | Alta |
| RF-006-05 | El sistema debe ser usable en pantallas de 320 px sin scroll horizontal. | Alta |
| RF-006-06 | El sistema debe mostrar estados visuales distintos para correcto, incorrecto, activo y pendiente. | Alta |
| RF-006-07 | El foco de teclado debe ser visible en todos los controles. | Alta |
| RF-006-08 | Los iconos del toggle deben tener nombre accesible (`aria-label`). | Media |
| RF-006-09 | El sistema debe respetar `prefers-color-scheme` cuando no haya preferencia. | Media |
| RF-006-10 | El favicon y el título deben ser consistentes en todas las páginas. | Baja |

## 5. Reglas de negocio y validaciones

| Regla | Comportamiento |
| --- | --- |
| Clave de tema | `localStorage["theme"]` con valores `dark` o `light`. |
| Atributo | `data-theme` en `<html>`. |
| Tema por defecto | `dark`, salvo `prefers-color-scheme: light` sin preferencia guardada. |
| Tokens | `--bg-primary`, `--bg-secondary`, `--text-main`, `--text-sub`, `--text-active`, `--caret`, `--success`, `--error`. |
| Contraste | Todo el texto ≥ 4.5:1 sobre su fondo (WCAG AA). |

## 6. Contratos

### Tokens CSS

| Token | Oscuro | Claro | Uso |
| --- | --- | --- | --- |
| `--bg-primary` | `#323437` | `#f5f5f5` | Fondo de página |
| `--bg-secondary` | `#2d3135` | `#e8e8e8` | Tarjetas y inputs |
| `--text-main` | `#d1d0c5` | `#323437` | Texto principal |
| `--text-sub` | `#9a9ca1` | `#5f6165` | Texto secundario |
| `--text-active` | `#d1d0c5` | `#323437` | Énfasis |
| `--caret` | `#d1d0c5` | `#323437` | Cursor y CTA |
| `--success` | `#9ece9a` | `#2e7d32` | Carácter correcto |
| `--error` | `#e58a90` | `#c0392b` | Carácter incorrecto |

### Estructura de plantilla propuesta

```text
templates/base.html
├── head (Tailwind config, fuentes, css)
├── header (logo, nav, toggle)
├── {% block content %}
├── footer
└── script de tema
```

## 7. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-006-01 | Sin parpadeo de tema (FOUC): script inline antes del `<body>`. |
| RNF-006-02 | CSS propio < 15 KB sin comprimir. |
| RNF-006-03 | Sin `outline: none` global sin reemplazo accesible. |
| RNF-006-04 | Tipografía `JetBrains Mono` con fallback a `monospace`. |

## 8. Criterios de aceptación

- **CA-006-01** Dado un usuario nuevo, cuando abre `/`, entonces ve tema oscuro.
- **CA-006-02** Dado que activo el tema claro, cuando recargo o navego a `/profile`, entonces sigue claro.
- **CA-006-03** Dado un viewport de 320 px, entonces no hay scroll horizontal en ninguna página.
- **CA-006-04** Dado navegación con Tab, entonces el foco es visible en logo, toggle, inputs y botones.
- **CA-006-05** Dado el toggle, cuando lo inspecciono con lector de pantalla, entonces anuncia "Toggle theme".
- **CA-006-06** Dado un cambio de token en `base.html`, entonces se refleja en las cuatro páginas.

## 9. Fuera de alcance

- Temas personalizados por usuario en base de datos.
- Modo impresión.
- Internacionalización de textos.

## 10. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Tema duplicado en 4 plantillas | Inconsistencias | T006-04 |
| `*:focus { outline: none }` | Inaccesible | T006-05 |
| Tailwind por CDN | Warning de producción y dependencia de red | Resuelto: build local (2026-11-11) |
| `--text-sub` con bajo contraste en claro | WCAG | T006-12: resuelto (`#5f6165`) |
| `--text-sub` sobre `--bg-secondary` en oscuro | WCAG | T006-12: resuelto (`#9a9ca1`) |

## 11. Referencias de código

- `templates/index.html`, `login.html`, `signup.html`, `profile.html`
- `static/css/styles.css`
- `static/icon/icon.svg`
