# Plan técnico 009 — Auditoría de ciberseguridad y filtraciones

| Campo | Valor |
| --- | --- |
| Spec | `specs/009-cybersecurity/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Auditoría defensiva, reproducible y de solo lectura, apoyada en un escáner sin
dependencias y en los verificadores nativos de Django. El eje principal es **evitar que
un secreto o dato personal llegue a GitHub** y, si ya llegó, contener, rotar y purgar en
ese orden.

## 2. Artefactos

| Artefacto | Propósito | Acción |
| --- | --- | --- |
| `specs/tools/scan_secrets.py` | Detectar secretos y archivos sensibles sin revelar valores | Creado |
| `specs/templates/audit-report.md` | Informe homogéneo | Creado |
| `audits/security/` | Histórico de auditorías | Creado |
| `.gitignore` | Prevención de recurrencia | Actualizado |

## 3. Modelo de amenaza

### Activos

| Activo | Ubicación | Impacto si se filtra |
| --- | --- | --- |
| Emails y usuarios | `auth_user` | Spam, enumeración, phishing |
| Hashes de contraseña | `auth_user.password` | Crackeo offline, credential stuffing |
| Resultados de tests | `backend_typingtestresult` | Perfilado de actividad |
| `SECRET_KEY` | `.env` | Falsificación de sesiones y tokens |
| Cookies de sesión | Navegador | Secuestro de cuenta |
| Código y configuración | Repo GitHub | Reconocimiento para ataques |

### Actores

| Actor | Motivación | Capacidad |
| --- | --- | --- |
| Bot de escaneo | Encontrar secretos en repos públicos | Automática, minutos |
| Atacante oportunista | Tomar cuentas, datos | Media |
| Usuario curioso | Ver datos de otros (IDOR) | Baja |
| Atacante con la BD | Crackear hashes | Alta (offline) |

### Superficie de ataque

```text
GitHub público
├── commits e historial
├── archivos rastreados (BD, .env, .pyc)
├── releases y artefactos
└── Actions logs

Aplicación
├── /login (fuerza bruta, enumeración)
├── /signup (abuso, duplicados)
├── /profile (IDOR)
├── /save_typing_test_result (datos falsificados)
├── /get_python_function (entrada JSON)
└── /admin/ (acceso privilegiado)
```

## 4. Matriz de verificación

| Requisito | Automático | Manual | Evidencia |
| --- | --- | --- | --- |
| RF-009-03 secretos | `scan_secrets.py` | Revisar falsos positivos | patrón + archivo:línea |
| RF-009-04 archivos sensibles | `scan_secrets.py` | Revisar `.gitignore` | `git ls-files` |
| RF-009-05 historial | `scan_secrets.py --history` | `git log` por ruta | commit |
| RF-009-06 config Django | `check --deploy` | Tabla de controles | warning |
| RF-009-07 authZ | — | Checklist | `views.py:línea` |
| RF-009-08 inyección/XSS | `code_metrics.py` | Revisión de plantillas/JS | `archivo:línea` |
| RF-009-09 dependencias | `pip-audit` | `pip list --outdated` | CVE |
| RF-009-10 GitHub | — | Checklist de 10 puntos | captura/estado |
| RF-009-11 PII | Conteo SQL | Retención y logs | `count(*)` |
| RF-009-12 enmascarado | Revisión del informe | — | `<redacted>` |

## 5. Remediación de la fuga de la base de datos

> **Requiere autorización explícita del usuario.** No se ejecuta en la auditoría.

### 5.1 Contener

```bash
# Dejar de rastrear el archivo (no lo borra del disco)
git rm --cached syntax_sprint/db.sqlite3

# Dejar de rastrear bytecode
git rm -r --cached syntax_sprint/backend/__pycache__
git rm -r --cached syntax_sprint/backend/migrations/__pycache__
git rm -r --cached syntax_sprint/syntax_sprint/__pycache__
```

### 5.2 Rotar e invalidar

1. Generar un nuevo `SECRET_KEY` y actualizar el `.env` del servidor.
2. Reiniciar la aplicación: las sesiones existentes quedan invalidadas.
3. Forzar el cambio de contraseña de los usuarios afectados.
4. Si hay credenciales de correo, base de datos o proveedores, rotarlas también.

### 5.3 Purgar el historial

```bash
# Herramienta recomendada
pip install git-filter-repo
git filter-repo --path syntax_sprint/db.sqlite3 --invert-paths --force

# Reañadir el remoto y publicar la historia reescrita
git remote add origin <url-del-repo>
git push origin --force --all
git push origin --force --tags
```

Advertencias:

- Coordinar con colaboradores: todos deben re-clonar.
- Los forks y cachés de GitHub pueden conservar el objeto.
- Si el repo es público, asumir que la BD ya fue descargada.
- Hacer backup del repo antes de reescribir.

### 5.4 Verificar

```bash
python specs/tools/scan_secrets.py --history
git log --all --full-history --oneline -- syntax_sprint/db.sqlite3
```

El segundo comando debe devolver vacío tras la purga.

## 6. Endurecimiento de Django

```python
# settings.py — solo en producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"
```

Además:

- `DEBUG=False` obligatorio.
- `ALLOWED_HOSTS` explícito.
- `SECRET_KEY` de ≥ 50 caracteres aleatorios, sin prefijo `django-insecure-`.
- `AUTH_PASSWORD_VALIDATORS` aplicados en el registro.
- Logout por POST.
- Rate limiting en login (django-axes o middleware).
- `{% csrf_token %}` en toda página que haga POST por `fetch`.

## 7. Endurecimiento de GitHub

| Control | Acción |
| --- | --- |
| Secret scanning | Activar en Settings → Code security |
| Push protection | Activar para bloquear secretos |
| Dependabot alerts | Activar |
| Dependabot security updates | Activar |
| Branch protection | Requerir PR y CI en `main` |
| Actions | No imprimir secretos; usar `secrets` |
| Visibilidad | Si hay PII, pasar a privado hasta remediar |
| Historial | Purgar secretos ya publicados |
| Forks | Asumir que no se pueden limpiar |

## 8. Estrategia de verificación

| Nivel | Qué se prueba | Cómo |
| --- | --- | --- |
| Unitario | Patrones del escáner | Archivo temporal con secreto ficticio |
| Integración | Detección de `db.sqlite3` y `.pyc` | Ejecución real |
| Historial | Detección en commits antiguos | `--history` |
| Config | Warnings de Django | `check --deploy` |
| Manual | AuthZ, XSS, GitHub | Checklist firmado |
| Post-remediación | Historial limpio | `scan_secrets.py --history` |

### Prueba del escáner sin secretos reales

Crear un archivo temporal **no rastreado** con un valor ficticio, ejecutar el escáner y
comprobar que detecta el patrón. Borrarlo después. No usar valores con formato real
completo.

## 9. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| Un secreto real se imprime durante la auditoría | Media | Regla de enmascarado y revisión del informe |
| Purgar historial sin rotar | Media | Rotar siempre primero |
| Force-push rompe colaboradores | Media | Avisar y coordinar ventana |
| El repo sigue público con la BD en caché | Media | Pasar a privado + rotar |
| Falsos positivos bloquean el trabajo | Alta | Marcar `[FP]` y separar blockers |
| `pip-audit` no disponible | Media | Entorno aislado o revisión manual |

## 10. Orden de implementación

1. Ejecutar escaneo de contenido e historial (hecho).
2. Ejecutar `check --deploy` y clasificar (hecho).
3. Revisión manual de authZ/XSS/GitHub (pendiente).
4. Decidir remediación de `db.sqlite3` (bloqueado por decisión del usuario).
5. Rotar credenciales y purgar historial (bloqueado).
6. Endurecer settings y GitHub.
7. Reauditar y comparar.

## 11. Notas de operación

- El informe de una fuga activa **no se publica** hasta completar la rotación.
- Los conteos de la BD (`6 usuarios`, `31 resultados`) son metadatos; no se leen filas.
- Nunca se incluye un hash, email o token en el informe.
