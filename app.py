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
        devesa = db.query(models.Area).filter(models.Area.area_name == "DEVESA").first()
    # --- Canal AsisTEC (notificaciones del sistema) ---
    # Limpieza: eliminar área/canal legacy "ASISTEC" (solo debe existir "AsisTEC")
    old_asistec_area = db.query(models.Area).filter_by(area_name="ASISTEC").first()
    if old_asistec_area:
        old_channel = db.query(models.Channel).filter_by(area_id=old_asistec_area.area_id).first()
        if old_channel:
            db.query(models.Post).filter_by(channel_id=old_channel.channel_id).delete()
            db.query(models.Subscription).filter_by(channel_id=old_channel.channel_id).delete()
            db.delete(old_channel)
        db.delete(old_asistec_area)
        db.commit()
        print("Área/canal legacy 'ASISTEC' eliminados para mantener solo AsisTEC.")

    asistec_area = db.query(models.Area).filter_by(area_name="AsisTEC").first()
    if not asistec_area:
        asistec_area = models.Area(area_name="AsisTEC", is_major=False)
        db.add(asistec_area)
        db.commit()
        db.refresh(asistec_area)
        print(f"Área AsisTEC creada (area_id={asistec_area.area_id})")
    else:
        print("Área AsisTEC ya existe, omitiendo creación.")

    # Buscar el canal siempre por nombre para evitar UniqueViolation al renombrar
    asistec_channel = db.query(models.Channel).filter_by(channel_name="Canal AsisTEC").first()
    if not asistec_channel:
        asistec_channel = models.Channel(
            channel_name="Canal AsisTEC", area_id=asistec_area.area_id
        )
        db.add(asistec_channel)
        db.commit()
        db.refresh(asistec_channel)
        print(f"Canal AsisTEC creado (channel_id={asistec_channel.channel_id})")
    else:
        if asistec_channel.area_id != asistec_area.area_id:
            asistec_channel.area_id = asistec_area.area_id
            db.commit()
            db.refresh(asistec_channel)
        print("Canal AsisTEC ya existe, omitiendo creación.")

    # Suscribir usuarios existentes al canal AsisTEC
    if asistec_channel:
        all_users = db.query(models.User).all()
        for u in all_users:
            exists = db.query(models.Subscription).filter_by(
                user_id=u.user_id, channel_id=asistec_channel.channel_id
            ).first()
            if not exists:
                db.add(models.Subscription(
                    user_id=u.user_id,
                    channel_id=asistec_channel.channel_id,
                    is_admin=False,
                    is_subscribed=True,
                ))
        db.commit()

    # --- Admin inicial ---
    admin = db.query(models.User).filter(models.User.mail == "admin@estudiantec.cr").first()
    if not admin:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        admin = models.User(
            name="Admin",
            lastname="Asistec",
            mail="admin@estudiantec.cr",
            password=pwd_context.hash("Admin#1"),
            carnet_number="20242417",
            gender="M",
            birth_date=datetime.date(1990, 1, 1),
            area_id=devesa.area_id if devesa else None,
            is_active=True,
            user_type="2",  # 2 = administrador
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Usuario admin creado: admin@estudiantec.cr / Admin#1")
    else:
        print("Usuario admin ya existe, omitiendo.")

    # Asegurar que el admin sea administrador del canal AsisTEC
    if asistec_channel and admin:
        sub = db.query(models.Subscription).filter_by(
            user_id=admin.user_id, channel_id=asistec_channel.channel_id
        ).first()
        if not sub:
            db.add(models.Subscription(
                user_id=admin.user_id,
                channel_id=asistec_channel.channel_id,
                is_admin=True,
                is_subscribed=True,
            ))
            db.commit()
        elif not sub.is_admin:
            sub.is_admin = True
            db.commit()


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
