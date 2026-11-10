# Plan técnico 00X — Nombre de la funcionalidad

| Campo | Valor |
| --- | --- |
| Spec | `specs/00X-nombre/spec.md` |
| Estado | Borrador / Aprobado |
| Autor | — |
| Última revisión | AAAA-MM-DD |

## 1. Enfoque

Resumen en 3–5 frases de la solución elegida.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `backend/views.py` | Modificar | ... |
| `backend/tests.py` | Añadir | ... |

## 3. Diseño de datos

```text
Modelo
├── campo: tipo (restricciones)
└── ...
```

Migración necesaria: sí/no. Reversible: sí/no.

## 4. Contratos y flujos

```text
Cliente → POST /ruta → Vista → Servicio → Modelo → Respuesta
```

Ejemplo de petición/respuesta cuando aplique.

## 5. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |

## 6. Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
| --- | --- | --- |
| Unitario | ... | `TestCase` |
| Integración | ... | `Client` |
| Manual | ... | Checklist |

## 7. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |

## 8. Orden de implementación

1. ...
2. ...

## 9. Notas de despliegue

- Migraciones: ...
- Variables de entorno: ...
- Estáticos: ...
