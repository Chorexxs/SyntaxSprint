# Plan técnico 005 — Resultados, perfil e historial

| Campo | Valor |
| --- | --- |
| Spec | `specs/005-results-and-profile/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Endurecer el endpoint de guardado con un parser y validador explícitos, simplificar el
cálculo de promedios a una sola consulta y paginar el historial. No se cambia el modelo
ni se requiere migración; los límites se aplican en la capa de vista para mantener la
base de datos portable.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `backend/views.py` | Modificar | `_parse_result_payload`, validación de rangos, `require_POST`, una sola agregación. |
| `backend/models.py` | Sin cambios | Se mantiene el esquema actual. |
| `templates/profile.html` | Modificar | Paginación, fecha localizada, tabla responsive. |
| `backend/tests.py` | Añadir | Tests de guardado, validación, aislamiento y promedios. |

## 3. Diseño de datos

Sin migración. Opcional a futuro: `language` y `duration` en el modelo (requiere nueva
migración y actualizar el contrato del endpoint).

```text
TypingTestResult
├── id: BigAutoField
├── user_id: FK auth_user (CASCADE)
├── wpm: float
├── accuracy: float
└── date: datetime (auto_now_add, index por orden)
```

## 4. Validación propuesta

```python
def _parse_result_payload(request):
    try:
        data = json.loads(request.body or b"{}")
        wpm = float(data["wpm"])
        accuracy = float(data["accuracy"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None

    if not math.isfinite(wpm) or not 0 <= wpm <= 400:
        return None
    if not math.isfinite(accuracy) or not 0 <= accuracy <= 100:
        return None
    return wpm, accuracy
```

## 5. Perfil

```python
results_qs = TypingTestResult.objects.filter(user=request.user).order_by("-date")
stats = results_qs.aggregate(avg_wpm=Avg("wpm"), avg_accuracy=Avg("accuracy"))
paginator = Paginator(results_qs, 20)
page = paginator.get_page(request.GET.get("page"))
```

Contexto: `page_obj`, `avg_wpm`, `avg_accuracy`, manteniendo `results` como alias de
`page_obj` para no romper la plantilla.

## 6. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| `ModelForm` para validar | Reutiliza validadores | El cliente envía JSON, no formulario | No |
| Validadores en el modelo | Consistencia en admin | Requiere migración y afecta datos históricos | No (por ahora) |
| Recalcular WPM en servidor | Anti-fraude | El servidor no ve el texto ni el tiempo real | Backlog con `duration` |
| Paginación por cursor | Eficiente | Complejo para el volumen actual | No |

## 7. Estrategia de pruebas

| Caso | Entrada | Esperado |
| --- | --- | --- |
| Guardado válido | 60 / 95 | 200, 1 fila |
| Sin sesión | 60 / 95 | 302 a login, 0 filas |
| GET | — | 405 |
| JSON inválido | `b"{"` | 400 |
| Faltan claves | `{"wpm": 60}` | 400 |
| Tipos no numéricos | `"60"` string | 200 si se acepta coerción; documentar |
| WPM negativo | -1 | 400 |
| Accuracy > 100 | 101 | 400 |
| Valores no finitos | `NaN`, `Infinity` | 400 |
| Aislamiento | dos usuarios | cada uno ve solo lo suyo |
| Promedios | 60/90 y 80/100 | 70 / 95 |
| Sin resultados | — | 0 / 0 y estado vacío |
| Cascada | borrar usuario | 0 filas |

## 8. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| Romper el contrato al rechazar strings | Media | Aceptar coerción numérica y documentarlo |
| Paginación cambia el contexto de la plantilla | Baja | Mantener `results` como alias |
| `math.isfinite` con `Decimal` | Baja | Convertir a `float` antes |
| Datos históricos fuera de rango | Baja | No validar en lectura, solo en escritura |

## 9. Orden de implementación

1. `require_POST` y parser defensivo.
2. Validación de rangos.
3. Agregación única y paginación.
4. Plantilla con paginación y estado vacío.
5. Tests.

## 10. Notas de despliegue

- Sin migraciones.
- No requiere cambios de configuración.
