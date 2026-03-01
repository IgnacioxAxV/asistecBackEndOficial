## Puesta en marcha rápida

### 1) Requisitos

- Python 3.10+
- El entorno virtual `.venv` ya está creado en la raíz del proyecto con todas las dependencias instaladas.

### 2) Ejecutar el servidor

**Windows:**
```bash
.venv\Scripts\python run_server.py
```

**Linux / Mac:**
```bash
.venv/bin/python run_server.py
```

El servidor arranca con Uvicorn en modo recarga en `http://0.0.0.0:8000`.

### 3) Variables de entorno

Copia `env.example` a `.env` y rellena los valores si quieres usar PostgreSQL:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
POSTGRES_DB=asistec
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Opciones:
- Si las variables de Postgres están definidas y la conexión es exitosa, se usará PostgreSQL.
- Si no hay Postgres disponible (o las variables están vacías), el backend cae automáticamente en SQLite local (`asistec.db`).
- Por defecto en desarrollo se usa SQLite sin necesidad de configuración adicional.

### 4) Pruebas

```bash
.venv/Scripts/python -m pytest tests/
# Linux/Mac:
.venv/bin/python -m pytest tests/
```

### Notas

- El servidor arranca con recarga automática (`--reload`).
- La base de datos SQLite se crea como `asistec.db` en la raíz del proyecto si no hay Postgres disponible.

### Resetear la base de datos (SQLite)

Si la DB ya existe (`asistec.db`), el seed inicial (Areas, admin, etc.) **no se vuelve a ejecutar**. Para resetear todo desde cero:

```bash
# Borrar la DB
rm asistec.db          # Linux/Mac
del asistec.db         # Windows

# Reiniciar el backend — recrea las tablas y ejecuta el seed automáticamente
.venv\Scripts\python run_server.py   # Windows
.venv/bin/python run_server.py       # Linux/Mac
```
