# Spec 007 — Calidad, seguridad y despliegue

| Campo | Valor |
| --- | --- |
| Estado | Pendiente |
| Versión | 1.0 |
| Depende de | 001…006 |
| Archivos principales | `backend/tests.py`, `settings.py`, `requirements.txt`, `README.md`, `.github/workflows/` |

## 1. Contexto y problema

El proyecto funciona en desarrollo, pero no tiene pruebas automatizadas, no pasa por un
pipeline de verificación, la configuración de producción es incompleta y la documentación
no coincide con el código. Esto hace que cada cambio sea riesgoso y que el despliegue
dependa de pasos manuales no documentados.

## 2. Objetivos

1. Suite de pruebas del backend con ≥ 80 % de cobertura.
2. Lint e imports verificados automáticamente.
3. Configuración de producción segura y reproducible.
4. Pipeline de CI que ejecute todo en cada push.
5. Documentación alineada con el estado real.

### No objetivos

- Migrar a PostgreSQL (backlog).
- Contenerizar la aplicación (backlog).
- Observabilidad avanzada (Sentry, métricas).
- Pentesting formal.

## 3. Actores y casos de uso

| Actor | Caso de uso |
| --- | --- |
| Desarrollador | Ejecutar tests y lint antes de integrar. |
| Revisor | Verificar el DoD en la PR. |
| Operador | Desplegar con un checklist reproducible. |

## 4. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-007-01 | El sistema debe tener pruebas de modelos, vistas y autenticación. | Alta |
| RF-007-02 | Cuando se ejecuta `manage.py test`, todos los tests deben pasar sin red. | Alta |
| RF-007-03 | El proyecto debe pasar `isort --check-only` y `pylint` sin errores nuevos. | Alta |
| RF-007-04 | Cuando llega JSON inválido a cualquier endpoint, el sistema debe responder 400, no 500. | Alta |
| RF-007-05 | En producción (`DEBUG=False`) el sistema debe usar HTTPS, cookies seguras y HSTS. | Alta |
| RF-007-06 | Ningún endpoint debe aceptar métodos no declarados. | Media |
| RF-007-07 | El despliegue debe ejecutar migraciones y `collectstatic` de forma reproducible. | Alta |
| RF-007-08 | La documentación (`README`, `AGENTS`, `specs`) debe coincidir con el código. | Media |
| RF-007-09 | La portada debe inicializar el token CSRF para permitir el POST de snippets. | Alta |
| RF-007-10 | El sistema debe servir estáticos en producción sin depender de `runserver`. | Alta |
| RF-007-11 | El pipeline debe ejecutarse en cada push y PR a `main`. | Media |

## 5. Reglas de negocio y validaciones

| Regla | Comportamiento |
| --- | --- |
| `DEBUG=False` | `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`. |
| `SECRET_KEY` | Obligatoria; sin valor por defecto. |
| Pruebas | Base de datos de test aislada; nunca tocar `db.sqlite3` real. |
| Cobertura | `coverage report --fail-under=80` en CI. |
| Lint | `pylint --fail-under=8` o lista de errores permitidos documentada. |
| Migraciones | `makemigrations --check --dry-run` en CI. |

## 6. Contratos y artefactos

| Artefacto | Contenido |
| --- | --- |
| `backend/tests.py` | Tests de auth, snippets, resultados, perfil y rutas. |
| `.github/workflows/ci.yml` | lint + check + migrations + tests. |
| `.env.example` | Variables documentadas. |
| `README.md` | Instalación, estructura y despliegue reales. |
| `specs/traceability.md` | Requisito → tarea → prueba. |

## 7. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-007-01 | La suite completa debe tardar < 60 s. |
| RNF-007-02 | Cobertura de `backend/views.py` y `backend/models.py` ≥ 80 %. |
| RNF-007-03 | El deploy debe poder revertirse con la versión anterior del código. |
| RNF-007-04 | Sin secretos en logs ni en respuestas HTTP. |

## 8. Criterios de aceptación

- **CA-007-01** Dado el repositorio limpio, cuando ejecuto `python manage.py test`, entonces pasan todos los tests.
- **CA-007-02** Dado un cambio que rompe una vista, cuando abro la PR, entonces CI falla.
- **CA-007-03** Dado `DEBUG=False`, cuando accedo por HTTP, entonces soy redirigido a HTTPS.
- **CA-007-04** Dado `collectstatic`, entonces `staticfiles/` contiene CSS, JS e icono.
- **CA-007-05** Dado un cuerpo JSON inválido en ambos endpoints, entonces la respuesta es 400.
- **CA-007-06** Dado `makemigrations --check`, entonces no hay migraciones pendientes.
- **CA-007-07** Dado el README, entonces la estructura descrita existe en el repo.

## 9. Fuera de alcance

- Cobertura de frontend.
- Pruebas de carga.
- Auditoría de dependencias automatizada (backlog con Dependabot).

## 10. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Activar HTTPS sin proxy correcto | Redirección infinita | Usar `SECURE_PROXY_SSL_HEADER` |
| `SECURE_HSTS_SECONDS` alto prematuro | Dominio bloqueado | Empezar en 3600 y subir |
| Tests dependientes de hora | Fallos intermitentes | `freezegun` o `mock` de `timezone.now` |
| Sin CI el DoD no se cumple | Regresiones | T007-07 |
| Tailwind CDN bloqueado por CSP | Estilos rotos | Resuelto: Tailwind compilado localmente (2026-11-11) |

## 11. Referencias de código

- `backend/tests.py` (vacío)
- `syntax_sprint/syntax_sprint/settings.py`
- `requirements.txt`
- `README.md`
- `.gitignore`
