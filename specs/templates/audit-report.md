# Plantilla de informe de auditoría

| Campo | Valor |
| --- | --- |
| Tipo | Código / Ciberseguridad |
| Fecha | AAAA-MM-DD |
| Auditor | — |
| Alcance | Repo completo / ruta / módulo |
| Commit auditado | `______` |
| Herramientas | — |
| Resultado global | A / B / C / D / F · CRÍTICO / ALTO / MEDIO / BAJO |

## 1. Alcance y exclusiones

- Incluido: ...
- Excluido: ...

## 2. Resumen ejecutivo

3–6 frases con los riesgos principales y la recomendación inmediata.

## 3. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Esfuerzo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUD-001 | ALTA | ... | `archivo.py:12` | comando o fragmento | ... | ... | S/M/L | Abierto |

> Regla: sin `archivo:línea` ni comando reproducible, el hallazgo no es válido.
> En seguridad, nunca incluir el valor del secreto; usar `<redacted>`.

## 4. Métricas

| Métrica | Valor | Umbral | Estado |
| --- | --- | --- | --- |
| ... | ... | ... | ✅/⚠️/❌ |

## 5. Comparación con la auditoría anterior

| Métrica | Anterior | Actual | Tendencia |
| --- | --- | --- | --- |

## 6. Acciones inmediatas (≤ 24 h)

1. ...

## 7. Tareas y specs creadas

| Hallazgo | Tarea | Spec |
| --- | --- | --- |
| AUD-001 | T00X-NN | `specs/00X-...` |

## 8. Comandos ejecutados

```bash
# Pegar comandos exactos y versión de las herramientas
```

## 9. Limitaciones

- ...
