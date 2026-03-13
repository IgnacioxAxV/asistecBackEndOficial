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
- **SQLite (por defecto):** No hace falta instalar nada más. Con `USE_SQLITE=true` (o sin configurar Postgres) se usa `asistec.db` en la raíz del backend. La misma configuración del proyecto (UUIDs, `profile_image`, canal AsisTEC, etc.) funciona con SQLite.
- **PostgreSQL:** Si defines las variables de Postgres y la conexión es correcta, se usará Postgres. Para crear la base desde cero usa el script `init_db.sql` (ver más abajo).

### 4) Pruebas

```bash
.venv/Scripts/python -m pytest tests/
# Linux/Mac:
.venv/bin/python -m pytest tests/
```

### Notas

- El servidor arranca con recarga automática (`--reload`).
- La base de datos SQLite se crea como `asistec.db` en la raíz del proyecto si no hay Postgres disponible.

### Usar la nueva configuración con SQLite (sin Postgres)

La configuración actual (UUIDs, `profile_image`, canal AsisTEC, admin, etc.) funciona con **SQLite** sin instalar Postgres. El backend crea las tablas con el esquema correcto y ejecuta el seed al arrancar.

Si ya tenías una base antigua (`asistec.db` con IDs numéricos), bórrala y arranca de nuevo para que se cree una SQLite nueva con UUIDs:

```bash
# 1. Borrar la DB antigua (desde la carpeta del backend)
del asistec.db         # Windows
# rm asistec.db        # Linux/Mac

# 2. Arrancar el backend — crea asistec.db nueva con el esquema actual y ejecuta el seed
.venv\Scripts\python run_server.py   # Windows
.venv/bin/python run_server.py       # Linux/Mac
```

Verás mensajes como "Área creada: ...", "Canal AsisTEC creado", "Usuario admin creado". A partir de ahí ya tienes la nueva configuración con SQLite.

### Resetear la base de datos (PostgreSQL) con `init_db.sql`

Cuando uses PostgreSQL y quieras recrear la base desde cero (por ejemplo tras borrar la DB), usa el script `init_db.sql`:

```bash
# 1. Crear la base de datos vacía
psql -U postgres -c "CREATE DATABASE asistec;"

# 2. Ejecutar el script (desde la raíz del backend)
psql -U postgres -d asistec -f init_db.sql

# 3. Arrancar el backend normalmente
.venv\Scripts\python run_server.py   # Windows
.venv/bin/python run_server.py       # Linux/Mac
```

El script incluye:
- Todas las tablas con sus columnas (incluye `profile_image` en `users`)
- Áreas semilla (carreras TEC San Carlos + AsisTEC)
- Canal AsisTEC enlazado al área
- Usuario admin (`admin@estudiantec.cr` / `Admin#1`) con suscripción al canal como administrador

**Nota:** El backend está alineado con este esquema: modelos con UUID (String(36)), `profile_image` en usuarios, restricción única (user_id, channel_id) en suscripciones y fechas DATE en actividades.
