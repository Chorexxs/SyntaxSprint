# Plan técnico 001 — Fundación del proyecto

| Campo | Valor |
| --- | --- |
| Spec | `specs/001-foundation/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Consolidar la configuración existente sin cambiar la arquitectura: limpiar rutas
heredadas, registrar el modelo en admin, eliminar imports duplicados y alinear las
versiones. Los cambios son de bajo riesgo y no requieren migraciones.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `syntax_sprint/syntax_sprint/settings.py` | Modificar | Quitar `BASE_DIR.parent/templates`; parsear `ALLOWED_HOSTS` de forma segura. |
| `syntax_sprint/backend/admin.py` | Modificar | Registrar `TypingTestResult` con `list_display`, `list_filter`, `search_fields`. |
| `syntax_sprint/backend/views.py` | Modificar | Eliminar bloque de imports duplicado (líneas 1–12 y 15–25) y símbolos sin usar. |
| `requirements.txt` | Modificar | Fijar una única versión de Django y verificar el resto. |
| `.env.example` | Crear | Documentar las tres variables sin valores reales. |
| `README.md` | Modificar | Corregir árbol de directorios (ver 007). |

## 3. Diseño de datos

Sin cambios de modelo. `TypingTestResult` ya existe en `0001_initial`.

```text
TypingTestResult
├── id: BigAutoField (PK)
├── user: FK → auth.User (CASCADE)
├── wpm: FloatField
├── accuracy: FloatField
└── date: DateTimeField (auto_now_add)
```

Migración necesaria: **no**.

## 4. Configuración de admin propuesta

```python
@admin.register(TypingTestResult)
class TypingTestResultAdmin(admin.ModelAdmin):
    list_display = ("user", "wpm", "accuracy", "date")
    list_filter = ("date", "user")
    search_fields = ("user__username", "user__email")
    ordering = ("-date",)
    date_hierarchy = "date"
```

## 5. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| Mantener la ruta de plantillas heredada | Cero cambios | Confusión y deuda | No |
| Mover plantillas a la raíz del repo | Coincide con el README | Rompe `BASE_DIR` y el despliegue actual | No |
| Leer configuración con `os.environ` | Sin dependencia | Menos ergonomía que `python-decouple` | No |

## 6. Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
| --- | --- | --- |
| Smoke | `manage.py check` | CLI |
| Integración | `/admin/` responde 302/200 según sesión | `TestCase` |
| Manual | El admin muestra y filtra resultados | Navegador |

## 7. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| Cambiar `ALLOWED_HOSTS` rompe el deploy | Media | Probar con el `.env` real antes de fusionar |
| El modelo en admin expone datos de usuarios | Baja | Solo accesible a `is_staff` |
| Eliminar imports rompe una vista | Baja | `manage.py check` + tests de 007 |

## 8. Orden de implementación

1. Limpiar imports en `views.py`.
2. Registrar el modelo en admin.
3. Corregir `settings.py` y crear `.env.example`.
4. Alinear `requirements.txt` y README.
5. Ejecutar `check` y pruebas.

## 9. Notas de despliegue

- No hay migraciones nuevas.
- `STATIC_ROOT` ya apunta a `staticfiles/`; ejecutar `collectstatic` en cada deploy.
- Verificar que el `.env` de producción tenga `DEBUG=False`.
