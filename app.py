import datetime
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from passlib.context import CryptContext
from database import engine, Base, get_db
from routes import router as api_router
from controllers.areas_controllers import create_area
import schemas
import models


def _seed(db):
    # Áreas iniciales
    initial_areas = [
        {"area_name": "DEVESA", "is_major": False},
        {"area_name": "Escuela Ciencias Naturales y Exactas San Carlos", "is_major": False},
        {"area_name": "Escuela de Ciencias del Lenguaje San Carlos", "is_major": False},
        {"area_name": "Dirección de Campus Tecnológico Local San Carlos", "is_major": False},
        {"area_name": "Ing. En Computación San Carlos", "is_major": True},
        {"area_name": "Ing. Electrónica San Carlos", "is_major": True},
        {"area_name": "Ing. Producción Industrial San Carlos", "is_major": True},
        {"area_name": "Ing. Agronomía San Carlos", "is_major": True},
        {"area_name": "Administración de Empresas San Carlos", "is_major": True},
        {"area_name": "Gestión del Turismo Rural Sostenible San Carlos", "is_major": True},
        {"area_name": "Gestión en Sostenibilidad Turística Sostenible San Carlos", "is_major": True},
    ]
    for area_data in initial_areas:
        try:
            create_area(schemas.AreaBase(**area_data), db)
            print(f"Área creada: {area_data['area_name']}")
        except Exception as e:
            print(f"Área omitida: {area_data['area_name']} ({e})")

    # Admin inicial (solo si no existe) -> esto se debe de quitar despues de empezar en producción, es solo para pruebas iniciales
    if not db.query(models.User).filter(models.User.mail == "admin@estudiantec.cr").first():
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        admin = models.User(
            name="Admin",
            lastname="Asistec",
            mail="admin@estudiantec.cr",
            password=pwd_context.hash("Admin#1"),
            carnet_number="20242417",
            gender="M",
            birth_date=datetime.date(1990, 1, 1),
            area_id=1,  # DEVESA
            is_active=True,
            user_type=2,  # 2 = administrador
        )
        db.add(admin)
        db.commit()
        print("Usuario admin creado: admin@estudiantec.cr / Admin#1")
    else:
        print("Usuario admin ya existe, omitiendo.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        _seed(db)
    finally:
        db.close()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "API FUNCIONANDO"}
