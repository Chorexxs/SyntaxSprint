# Spec 000 — Visión de producto: SyntaxSprint

| Campo | Valor |
| --- | --- |
| Estado | Implementada (backlog en `tasks.md`) |
| Versión | 1.0 |
| Depende de | — |
| Archivos principales | `syntax_sprint/`, `backend/`, `templates/`, `static/` |

## 1. Contexto y problema

Las personas que programan escriben código más rápido y con menos errores cuando
practican mecanografía sobre sintaxis real. Los tests de mecanografía genéricos usan
texto natural, no código, por lo que no entrenan símbolos, indentación ni atajos
propios de un lenguaje.

**SyntaxSprint** ofrece tests de velocidad de escritura de 30 segundos sobre fragmentos
de código reales en ocho lenguajes, calcula WPM y precisión, y guarda el historial del
usuario para medir su progreso.

## 2. Objetivos

1. Permitir practicar mecanografía con fragmentos de código de 8 lenguajes.
2. Medir WPM y precisión de forma consistente y comprensible.
3. Persistir cada resultado y mostrar historial y promedios por usuario.
4. Ofrecer una experiencia minimalista, rápida y con tema claro/oscuro.
5. Funcionar con una pila sencilla y desplegable: Django + PostgreSQL (InsForge) + Gunicorn.

### No objetivos

- Competencia multijugador en tiempo real.
- Corrección o ejecución del código escrito.
- Aplicación móvil nativa.
- Gestión de equipos, roles o planes de pago.
- Sincronización con teclados o hardware externo.

## 3. Actores y casos de uso

| Actor | Casos de uso |
| --- | --- |
| Visitante | Ver la portada, elegir lenguaje, hacer un test, registrarse, iniciar sesión. |
| Usuario autenticado | Hacer tests, guardar resultados, consultar perfil, promedios e historial, cerrar sesión. |
| Administrador | Gestionar usuarios y resultados desde Django Admin. |

## 4. Capacidades del producto

| ID | Capacidad | Spec | Estado |
| --- | --- | --- | --- |
| C1 | Configuración del proyecto y del entorno | `001-foundation` | Implementada |
| C2 | Registro, login, logout y sesiones | `002-authentication` | Implementada |
| C3 | Catálogo y entrega de fragmentos de código | `003-snippet-service` | Implementada |
| C4 | Motor de test de mecanografía | `004-typing-engine` | Implementada |
| C5 | Persistencia de resultados, perfil e historial | `005-results-and-profile` | Implementada |
| C6 | Sistema visual, temas y responsividad | `006-ui-and-theming` | Implementada |
| C7 | Calidad, pruebas, seguridad y despliegue | `007-quality-and-delivery` | Implementada |
| C8 | Auditoría de código y arquitectura bajo demanda | `008-code-audit` | Implementada (procedimiento) |
| C9 | Auditoría de ciberseguridad y filtraciones bajo demanda | `009-cybersecurity` | Implementada (procedimiento) |
| C10 | Inventario y actualización de dependencias bajo demanda | `010-dependencies` | Implementada (procedimiento) |

## 5. Requisitos funcionales de producto

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-000-01 | El sistema debe mostrar una portada pública con selector de lenguaje y botón de inicio. | Alta |
| RF-000-02 | El sistema debe permitir registrarse, iniciar y cerrar sesión. | Alta |
| RF-000-03 | El sistema debe entregar un fragmento aleatorio del lenguaje elegido. | Alta |
| RF-000-04 | El sistema debe medir WPM y precisión durante 30 segundos. | Alta |
| RF-000-05 | El sistema debe guardar el resultado del usuario autenticado. | Alta |
| RF-000-06 | El sistema debe mostrar historial y promedios en el perfil. | Alta |
| RF-000-07 | El sistema debe recordar el tema claro/oscuro elegido. | Media |
| RF-000-08 | El sistema debe ser usable en escritorio y móvil. | Media |
| RF-000-09 | Cuando el usuario lo solicite, el sistema debe auditar el código y la arquitectura con evidencia verificable. | Media |
| RF-000-10 | Cuando el usuario lo solicite, el sistema debe auditar la seguridad y detectar filtraciones sin revelar secretos. | Alta |

## 6. Requisitos no funcionales globales

| ID | Requisito |
| --- | --- |
| RNF-000-01 | Tiempo de respuesta del endpoint de fragmentos < 300 ms en local. |
| RNF-000-02 | El test debe funcionar en navegadores modernos con soporte ES6. |
| RNF-000-03 | Ningún secreto debe estar en el repositorio. |
| RNF-000-04 | Cobertura de pruebas del backend ≥ 80 % al cerrar la v0.2. |
| RNF-000-05 | El sitio debe cumplir contraste WCAG AA en ambos temas. |
| RNF-000-06 | El código debe pasar `pylint` e `isort` sin errores nuevos. |

## 7. Métricas de éxito

| Métrica | Objetivo |
| --- | --- |
| Tests completados por usuario activo | ≥ 3 por semana |
| Error rate de la API de fragmentos | < 1 % |
| Usuarios que guardan al menos un resultado | ≥ 60 % de registrados |
| Lighthouse Performance (portada) | ≥ 90 |

## 8. Glosario

| Término | Definición |
| --- | --- |
| **WPM** | Palabras por minuto. `(caracteres correctos / 5) / minutos transcurridos`. |
| **Precisión** | `caracteres correctos / caracteres totales × 100`. |
| **Fragmento** | Snippet de código de un lenguaje concreto. |
| **Test** | Sesión de 30 s escribiendo un fragmento. |
| **Resultado** | Registro de WPM y precisión de un test. |
| **AFK** | Away From Keyboard: segundo sin pulsaciones. |

## 9. Fuera de alcance (v1)

- Multijugador, ranking global y ligas.
- Cuentas sociales (OAuth).
- Internacionalización de la interfaz.
- Notificaciones o correo transaccional.

## 10. Riesgos de producto

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Fragmentos demasiado largos para 30 s | Mala experiencia | Limitar a ≤ 15 líneas; validar en tests manuales |
| Guardado silencioso fallido | Pérdida de progreso | Mostrar estado y registrar errores (ver 005) |
| Dependencia de CDN de Tailwind | Caída del CDN rompe estilos | Resuelto: build local (2026-11-11) |
| Sin pruebas automatizadas | Regresiones frecuentes | Resuelto: 39 tests y 99 % de cobertura (T007-01…T007-05) |

## 11. Referencias

- `README.md` — descripción funcional y de instalación.
- `AGENTS.md` — guía de desarrollo y flujo SDD.
- `specs/traceability.md` — trazabilidad completa.
