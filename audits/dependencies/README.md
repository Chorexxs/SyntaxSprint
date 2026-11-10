# Informes de dependencias

Un informe por ejecución del procedimiento de `specs/010-dependencies/spec.md`.

## Estructura

```text
audits/dependencies/
└── AAAA-MM-DD-actualizacion.md
```

## Reglas

1. Un informe por ejecución, con fecha y commit de partida.
2. No incluir secretos, tokens ni valores de `.env`.
3. Toda afirmación va acompañada del comando que la respalda.
4. Separar lo aplicado de lo pendiente y de lo descartado.
5. Registrar las reversiones con su motivo.
6. El informe se escribe en español.

## Formato

1. Metadatos: fecha, commit, entorno y alcance.
2. Inventario: paquete, versión actual, última, tipo y acción.
3. Seguridad: resultado de `pip-audit`.
4. Grupos aplicados: parches y menores.
5. Pendientes: actualizaciones mayores y su justificación.
6. Verificación: comandos y resultados.
7. Reversiones.
8. Riesgos abiertos.
