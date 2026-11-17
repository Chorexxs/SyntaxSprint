# Auditorías de SyntaxSprint

Histórico de auditorías bajo demanda definidas en:

- `specs/008-code-audit/` — calidad, arquitectura y escalabilidad.
- `specs/009-cybersecurity/` — seguridad, secretos y filtraciones.
- `specs/010-dependencies/` — inventario y actualización de dependencias.

## Estructura

```text
audits/
├── code/
│   └── AAAA-MM-DD-alcance.md
├── dependencies/
│   └── AAAA-MM-DD-actualizacion.md
└── security/
    └── AAAA-MM-DD-alcance.md
```

## Reglas

1. Un informe por ejecución, con fecha y commit auditado.
2. Usar `specs/templates/audit-report.md`.
3. Todo hallazgo lleva `archivo:línea` o comando reproducible.
4. **Nunca** incluir valores de secretos, contraseñas, tokens ni datos personales.
5. Los hallazgos CRÍTICOS de seguridad se enlazan a su tarea de remediación.
6. El informe se escribe en español.
7. Los informes se publican junto al repositorio (que es público): no incluyen
   valores de secretos, contraseñas, tokens ni PII directa (regla 4).

## Línea base

| Fecha | Tipo | Informe | Resultado |
| --- | --- | --- | --- |
| 2026-11-10 | Código | `code/2026-11-10-linea-base.md` | 3.8/10 (F) |
| 2026-11-10 | Seguridad | `security/2026-11-10-linea-base.md` | CRÍTICO |
| 2026-11-10 | Seguridad | `security/2026-11-10-auditoria-completa.md` | Contenido — producción verificada |
| 2026-11-10 | Dependencias | `dependencies/2026-11-10-actualizacion.md` | 0 vulnerabilidades; parches aplicados |
| 2026-11-11 | Código | `code/2026-11-11-reauditoria.md` | 8.8/10 (B); 0 hallazgos ALTA |
| 2026-11-11 | Seguridad | `security/2026-11-11-verificacion.md` | PII y secretos cerrados; quedan acciones del responsable |
| 2026-11-11 | Código | `code/2026-11-11-auditoria-post-analitica.md` | 8.55/10 (B); 0 ALTA |
| 2026-11-11 | Seguridad | `security/2026-11-11-auditoria-post-analitica.md` | MEDIO; 0 CRÍTICAS/ALTAS, 3 MEDIAS |
| 2026-11-11 | Código | `code/2026-11-11-auditoria-post-2fa.md` | 8.25/10 (B); 0 ALTA, 2 MEDIA |
| 2026-11-12 | Código | `code/2026-11-12-reauditoria.md` | 8.9/10 (B); 0 ALTA, 1 MEDIA (tooling) |
| 2026-11-12 | Código | `code/2026-11-12-auditoria-arquitectura.md` | 8.6/10 (B); 0 ALTA, 2 MEDIA y 2 BAJA |
| 2026-11-12 | Seguridad | `security/2026-11-12-auditoria-prepublicacion.md` | BAJO; 0 CRÍTICAS/ALTAS, 4 BAJAS (2 cerradas, 2 aceptadas) |

> El historial está purgado, GitHub Pages devuelve 404 y la `SECRET_KEY` de producción
> está rotada. Las API keys de Render e InsForge se revocaron el 2026-11-11 y el reset
> de contraseñas no aplicaba (0 cuentas en producción). El repositorio es **público**
> desde esa revisión y sus ajustes de GitHub se verificaron el 2026-11-17 (`T009-39`).
>
> Remediación 2026-11-11: SEC-016…SEC-021 y AUD-013…AUD-015 cerrados en el mismo día
> del informe; queda AUD-016 (INFO). Después se añadieron caché compartida del rate
> limit y 2FA del admin (spec 012).
