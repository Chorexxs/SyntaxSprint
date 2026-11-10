# Auditorías de SyntaxSprint

Histórico de auditorías bajo demanda definidas en:

- `specs/008-code-audit/` — calidad, arquitectura y escalabilidad.
- `specs/009-cybersecurity/` — seguridad, secretos y filtraciones.

## Estructura

```text
audits/
├── code/
│   └── AAAA-MM-DD-alcance.md
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

## Línea base

| Fecha | Tipo | Informe | Resultado |
| --- | --- | --- | --- |
| 2026-11-10 | Código | `code/2026-11-10-linea-base.md` | 3.8/10 (F) |
| 2026-11-10 | Seguridad | `security/2026-11-10-linea-base.md` | CRÍTICO |
| 2026-11-10 | Seguridad | `security/2026-11-10-auditoria-completa.md` | CRÍTICO — contención local aplicada |

> El informe de auditoría completa **no debe publicarse ni commitearse** hasta completar
> la rotación de credenciales y la purga del historial (`RNF-009-05`).
