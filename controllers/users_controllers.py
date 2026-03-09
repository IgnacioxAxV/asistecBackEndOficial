# Standard library
import calendar
import json
from typing import Optional
from datetime import date, datetime, timedelta

# Third-party packages
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Internal modules
import models
import schemas


# Mapea días a números (Monday = 0)
weekday_map = {day.lower(): i for i, day in enumerate(calendar.day_name)}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_all_users(db: Session):
    return db.query(models.User).all()


def get_user_by_id(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def create_user(user: schemas.UserCreate, db: Session):
    # Verificar si ya existe el correo
    db_user = db.query(models.User).filter(models.User.mail == user.mail).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    # Verificar si ya existe el número de carné
    db_carnet = (
        db.query(models.User)
        .filter(models.User.carnet_number == user.carnet_number)
        .first()
    )
    if db_carnet:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Carnet number already registered",
        )

    # Crear el usuario
    hashed_password = pwd_context.hash(user.password)
    user_data = user.model_dump(exclude={"password"})
    new_user = models.User(**user_data, password=hashed_password)

    # ISSUE: la creación del usuario y la asignación de suscripciones primarias son
    # dos pasos lógicamente distintos que hoy comparten la misma transacción.
    # Se sugiere extraer el bloque de suscripciones a una función `primary_subscriptions(user, db)`
    # que reciba el usuario ya creado y se encargue exclusivamente de esa lógica,
    # mejorando la separación de responsabilidades y facilitando el testing independiente.

    db.add(new_user)
    db.flush()

    # 1. Suscribir al canal principal del área asignada
    main_channel = (
        db.query(models.Channel)
        .filter(models.Channel.area_id == new_user.area_id)
        .first()
    )
    if main_channel:
        db.add(
            models.Subscription(
                user_id=new_user.user_id,
                channel_id=main_channel.channel_id,
                is_admin=False,
                is_subscribed=True,
            )
        )

    # 2. Suscribir a los canales por defecto
    area_names = [
        "DEVESA",
        "Escuela de Ciencias Naturales y Exactas",
        "Escuela de Ciencias del Lenguaje",
        "AsisTEC",
    ]

    # Buscar los canales por nombre de área
    additional_channels = (
        db.query(models.Channel)
        .join(models.Area)
        .filter(models.Area.area_name.in_(area_names))
        .all()
    )

    for channel in additional_channels:
        db.add(
            models.Subscription(
                user_id=new_user.user_id,
                channel_id=channel.channel_id,
                is_admin=False,
                is_subscribed=True,
            )
        )

    # Un único commit garantiza que el usuario y sus suscripciones primarias
    # se persistan juntos; si algo falla, ninguno queda a medias en la DB.
    db.commit()
    db.refresh(new_user)

    return {"msg": "SUCCESS", "user_id": new_user.user_id}


def login_user(user: schemas.UserLogin, db: Session):
    db_user = db.query(models.User).filter(models.User.mail == user.mail).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if the user is active
    if not db_user.is_active:
        raise HTTPException(status_code=401, detail="Inactive")

    db_user.last_login = datetime.utcnow()
    db.commit()

    admin_channels = (
        db.query(models.Subscription.channel_id)
        .filter(models.Subscription.user_id == db_user.user_id, models.Subscription.is_admin == True)
        .all()
    )

    return {
        "user_id": db_user.user_id,
        "email": db_user.mail,
        "full_name": f"{db_user.name} {db_user.lastname}",
        "area": db_user.area.area_name,
        "area_id": db_user.area_id,
        "user_type": db_user.user_type,
        "is_channel_admin": len(admin_channels) > 0,
    }


def parse_datetime(date_value, time_value):
    if isinstance(date_value, str):
        date_obj = datetime.strptime(date_value, "%Y-%m-%d").date()
    elif isinstance(date_value, datetime):
        date_obj = date_value.date()
    else:
        date_obj = date_value

    if isinstance(time_value, str):
        time_obj = datetime.strptime(time_value, "%H:%M").time()
    elif isinstance(time_value, datetime):
        time_obj = time_value.time()
    else:
        time_obj = time_value

    return datetime.combine(date_obj, time_obj)


def get_next_occurrence(
    start_date: date, final_date: date, schedule: dict
) -> Optional[tuple]:
    now = datetime.now()

    # Forzar tipos de fecha
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(final_date, datetime):
        final_date = final_date.date()

    for day_offset in range(0, 14):  # Buscar en los próximos 14 días
        check_date = now.date() + timedelta(days=day_offset)
        if not (start_date <= check_date <= final_date):
            continue

        weekday = check_date.weekday()
        for entry in schedule.values():
            scheduled_day = weekday_map.get(entry["date"].lower())
            if scheduled_day == weekday:
                start_time_str = entry["start_time"]
                start_time_dt = datetime.strptime(start_time_str, "%H:%M").time()

                # Comparar también la hora si el día es hoy
                if check_date == now.date() and start_time_dt <= now.time():
                    continue  # Ya pasó esa hora hoy

                return check_date, start_time_str

    return None


def get_user_next_activities(user_id: int, db: Session):
    today = date.today()
    upcoming = []

    # Eventos
    events = (
        db.query(models.Event)
        .filter(models.Event.user_id == user_id, models.Event.event_date >= today)
        .order_by(models.Event.event_date.asc())
        .all()
    )

    for e in events:
        upcoming.append(
            {
                "id": e.event_id,
                "type": "event",
                "title": e.event_title,
                "date": e.event_date.strftime("%Y-%m-%d"),  # ← date homogéneo
                "start_time": e.event_start_hour.strftime("%H:%M"),  # ← hora homogénea
                "location": getattr(e, "location", None),
            }
        )

    # Actividades
    activities = (
        db.query(models.Activity).filter(models.Activity.user_id == user_id).all()
    )

    for a in activities:
        schedule = json.loads(a.schedule)
        next_occurrence = get_next_occurrence(
            a.activity_start_date, a.activity_final_date, schedule
        )
        if next_occurrence:
            occ_date, start_time = next_occurrence
            if occ_date >= today:
                upcoming.append(
                    {
                        "id": a.activity_id,
                        "type": "activity",
                        "title": a.activity_title,
                        "date": occ_date,
                        "start_time": start_time,
                        "location": a.location,
                    }
                )

    # Ordenar por fecha y hora
    upcoming.sort(key=lambda x: parse_datetime(x["date"], x["start_time"]))

    return upcoming[:3]


def activate_user(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.is_active:
        return {"msg": "User is already active"}

    user.is_active = True
    db.commit()

    return {"msg": "User activated successfully"}
