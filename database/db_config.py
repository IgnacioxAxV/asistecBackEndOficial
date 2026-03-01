import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

def _build_engine():
    # Intentar conectar a PostgreSQL si las variables de entorno están definidas
    if all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
        postgres_url = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
        try:
            engine = create_engine(postgres_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Conectado a PostgreSQL correctamente.")
            return engine
        except Exception as e:
            print(f"No se pudo conectar a PostgreSQL: {e}")
            print("Usando SQLite como fallback...")

    # --- FALLBACK DESARROLLO ---
    # IMPORTANTE: Este bloque de SQLite es solo para desarrollo y pruebas locales.
    # Al pasar a producción en el servidor de la universidad, eliminar este fallback
    # y asegurarse de que las variables de entorno de PostgreSQL estén configuradas correctamente.
    sqlite_url = f"sqlite:///{os.path.join(BASE_DIR, 'asistec.db')}"
    print("Usando SQLite (modo desarrollo).")
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})
    # --- FIN FALLBACK DESARROLLO ---

engine = _build_engine()

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para inyectar sesión en rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
