# Spec 010 — Dependencias y actualización bajo demanda

| Campo | Valor |
| --- | --- |
| Estado | Implementada |
| Versión | 1.0 |
| Depende de | `000-overview`, `007-quality-and-delivery` |
| Archivos principales | `requirements.txt`, `render.yaml`, `.github/workflows/ci.yml`, `syntax_sprint/templates/*.html` |

## 1. Contexto y problema

Las dependencias de Python están fijadas con versión exacta en `requirements.txt`, pero
no existe ninguna política que diga **cuándo** ni **cómo** actualizarlas. Además:

- Conviven dependencias de producción y de desarrollo en el mismo archivo.
- `requests` y sus transitivas (`certifi`, `charset-normalizer`, `idna`, `urllib3`) no
  se usan en el código.
- El CDN de Tailwind no fijaba versión; desde el 2026-11-11 se compila localmente con
  `3.4.17` fijada en `package.json`.
- `pip-audit` se ejecutó una sola vez (`T009-18`) y no hay procedimiento repetible.
- La versión de Python vive en `render.yaml` y en el workflow de CI, sin una fuente única.

El resultado es que el proyecto se desfasa en silencio, acumula vulnerabilidades y cada
actualización se convierte en un salto grande y arriesgado.

## 2. Objetivos

1. Tener un inventario único y verificable de todas las dependencias del proyecto.
2. Ejecutar las actualizaciones **solo cuando el responsable lo pida**, con pasos
   reproducibles y evidencia.
3. Separar parches y versiones menores de las actualizaciones mayores.
4. Detectar vulnerabilidades con `pip-audit` en cada ejecución.
5. Dejar un informe versionado en `audits/dependencies/`.

### No objetivos

- Actualizaciones automáticas programadas (eso es Dependabot/Renovate, ver `T010-09`).
- Cambiar de gestor de paquetes (pip-tools, poetry, uv) sin una spec aparte.
- Actualizar el sistema operativo, PostgreSQL o el proveedor de hosting.
- Desplegar la aplicación.

## 3. Actores y casos de uso

| Actor | Caso de uso |
| --- | --- |
| Responsable del proyecto | Pide "revisa/actualiza las dependencias", aprueba mayores y decide eliminaciones. |
| Agente de IA | Ejecuta el inventario, aplica parches/menores y redacta el informe. |
| CI | Verifica que la actualización no rompe `check`, migraciones ni tests. |

## 4. Requisitos funcionales

> Formato EARS: *Cuando* <evento>, *el sistema debe* <comportamiento>.

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-010-01 | Cuando el responsable lo solicite, el sistema debe ejecutar el procedimiento de dependencias sin cambiar comportamiento de negocio. | Alta |
| RF-010-02 | Al iniciar, el sistema debe inventariar dependencias de Python, CDN, runtime, acciones de CI e infraestructura. | Alta |
| RF-010-03 | Al inventariar, el sistema debe comparar cada versión fijada con la última disponible y registrar el resultado. | Alta |
| RF-010-04 | Al inventariar, el sistema debe ejecutar `pip-audit` y registrar los avisos de seguridad encontrados. | Alta |
| RF-010-05 | Al clasificar, el sistema debe separar parches, menores, mayores y actualizaciones de seguridad. | Alta |
| RF-010-06 | Cuando haya actualizaciones de parche o menores, el sistema debe aplicarlas en una rama dedicada con versiones exactas. | Alta |
| RF-010-07 | Cuando haya actualizaciones mayores, el sistema debe aislarlas en una rama y una tarea propias, con aprobación previa. | Alta |
| RF-010-08 | Tras actualizar, el sistema debe ejecutar `check`, `makemigrations --check`, tests, `isort`, `pylint` y `collectstatic`. | Alta |
| RF-010-09 | Si la verificación falla, el sistema debe revertir el grupo afectado y documentar el motivo. | Alta |
| RF-010-10 | Al terminar, el sistema debe generar un informe con el antes y el después en `audits/dependencies/`. | Media |
| RF-010-11 | Si hay cambios sin commitear o la rama base no es `main`, el sistema debe detenerse antes de tocar dependencias. | Media |
| RF-010-12 | Al modificar `requirements.txt`, el sistema debe mantenerlo ordenado, sin duplicados y con versiones exactas. | Media |

## 5. Reglas de negocio y validaciones

| Regla | Comportamiento esperado |
| --- | --- |
| Solo bajo demanda | Nada se actualiza si el responsable no lo pide explícitamente. |
| Nunca a mitad de una funcionalidad | El árbol debe estar limpio y `main` sincronizado antes de empezar. |
| Parches y menores juntos, mayores aparte | Un commit y una rama por grupo; nunca mezclar. |
| Dependencia no usada | Se propone eliminarla, no actualizarla. |
| Versiones exactas | `requirements.txt` siempre con `==`; sin rangos flotantes. |
| Django | Se prefiere LTS; un salto mayor requiere plan y ventana de pruebas. |
| Secretos | El procedimiento nunca lee, imprime ni modifica valores de `.env`. |
| Un solo cambio por commit | Mensaje en español, formato `Actualizar: ...`. |

## 6. Contratos

### Comandos del procedimiento

| Paso | Comando |
| --- | --- |
| Inventario instalado | `pip list --format=freeze` |
| Versiones disponibles | `pip index versions <paquete>` o `pip list --outdated` |
| Vulnerabilidades | `pip-audit -r requirements.txt` |
| Verificación | `manage.py check`, `makemigrations --check --dry-run`, `manage.py test` |
| Estilo | `isort --check-only syntax_sprint/`, `pylint backend` |
| Estáticos | `manage.py collectstatic --noinput` |

### Informe

`audits/dependencies/AAAA-MM-DD-actualizacion.md` con:

1. Commit de partida y fecha.
2. Tabla de inventario (paquete, versión actual, última, tipo, acción).
3. Tabla de `pip-audit` (paquete, CVE, severidad, resolución).
4. Grupos aplicados (parches/menores) y mayores pendientes.
5. Verificación ejecutada con su resultado.
6. Reversiones y motivos.
7. Riesgos abiertos.

No se modifican endpoints ni modelos de datos.

## 7. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-010-01 | Una ejecución de parches y menores debe completarse en menos de 30 minutos. |
| RNF-010-02 | El procedimiento debe ser reproducible con los mismos comandos en cualquier máquina. |
| RNF-010-03 | El informe no debe contener secretos, tokens ni datos personales. |
| RNF-010-04 | El procedimiento no debe añadir dependencias de ejecución: usa pip y stdlib. |
| RNF-010-05 | `main` no puede quedar con CI rojo tras una actualización. |

## 8. Criterios de aceptación

- **CA-010-01** Dado `main` limpio, cuando el responsable pide revisar dependencias,
  entonces existe inventario y resultado de `pip-audit` sin cambios de código.
- **CA-010-02** Dado un grupo de parches aplicado, cuando se ejecuta la verificación,
  entonces `check`, migraciones, los 26 tests e `isort` terminan en verde.
- **CA-010-03** Dado un grupo que rompe las pruebas, cuando se detecta, entonces se
  revierte ese grupo y se documenta el motivo.
- **CA-010-04** Dada una actualización mayor, cuando se propone, entonces no se aplica
  en el mismo commit que los parches y requiere aprobación.
- **CA-010-05** Dado el informe final, cuando se revisa, entonces incluye antes/después
  y no contiene secretos.
- **CA-010-06** Dado que el responsable no lo ha pedido, cuando pasa el tiempo, entonces
  ninguna dependencia cambia.

## 9. Fuera de alcance

- Configurar Dependabot o Renovate (queda como `T010-09`).
- Migrar de `requirements.txt` a un lockfile generado.
- Actualizar la imagen de Python del proveedor de hosting.
- Auditar código o seguridad (specs `008` y `009`).

## 10. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Una actualización rompe comportamiento no cubierto | Regresión silenciosa | Verificación completa + checklist manual del test de typing |
| Salto mayor de Django (5.2 → 6.x) | Cambios incompatibles | Rama y tarea aparte, ventana de pruebas |
| CDN de Tailwind sin versión | Cambio de estilos sin aviso | Resuelto: build local con versión fijada (`T010-08`) |
| Actualizar por actualizar | Ruido y riesgo | Solo bajo demanda y con informe |
| Dependencias transitivas descontroladas | CVEs invisibles | `pip-audit` en cada ejecución y CI |
| Falsa sensación de seguridad | Deuda oculta | El informe lista lo que **no** se actualizó y por qué |

## 11. Referencias de código

- `requirements.txt` — dependencias de Python fijadas.
- `render.yaml` — versión de Python y variables de despliegue.
- `.github/workflows/ci.yml` — verificación automática.
- `syntax_sprint/templates/*.html` — clases de Tailwind y Google Fonts.
- `tailwind.config.js`, `package.json` y `assets/css/tailwind.input.css` — build local.
- `specs/009-cybersecurity/tasks.md` — `T009-18` (pip-audit) y `T009-19` (Dependabot).
- `audits/README.md` — reglas de los informes bajo demanda.
