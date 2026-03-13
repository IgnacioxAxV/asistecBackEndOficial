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


def get_user_by_id(user_id: str, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def _is_channel_admin_domain(email: str) -> bool:
    """Usuarios con correo @itcr.ac.cr son admins del canal de su área."""
    if not email:
        return False
    return email.lower().strip().endswith("@itcr.ac.cr")


def _ensure_primary_subscriptions(db_user: models.User, db: Session):
    # 1. Asegurar canal principal del área asignada (canal de la carrera).
    #    Solo usamos canales que YA existen; no creamos canales nuevos aquí.
    #    Usuarios con correo @itcr.ac.cr quedan como admins de ese canal.
    is_admin_area = _is_channel_admin_domain(db_user.mail or "")
    main_channel = None
    if db_user.area_id:
        # a) Intentar encontrar un canal ya asociado al área del usuario
        main_channel = (
            db.query(models.Channel)
            .filter(models.Channel.area_id == db_user.area_id)
            .first()
        )

        # b) Si no hay canal con area_id, buscar uno existente cuyo nombre contenga el nombre del área
        if not main_channel:
            area = db.query(models.Area).filter(models.Area.area_id == db_user.area_id).first()
            if area:
                like_pattern = f"%{area.area_name}%"
                main_channel = (
                    db.query(models.Channel)
                    .filter(models.Channel.channel_name.ilike(like_pattern))
                    .first()
                )
    if main_channel:
        exists = (
            db.query(models.Subscription)
            .filter_by(user_id=db_user.user_id, channel_id=main_channel.channel_id)
            .first()
        )
        if not exists:
            db.add(
                models.Subscription(
                    user_id=db_user.user_id,
                    channel_id=main_channel.channel_id,
                    is_admin=is_admin_area,
                    is_subscribed=True,
                )
            )
        else:
            if not exists.is_subscribed:
                exists.is_subscribed = True
            if is_admin_area:
                exists.is_admin = True

    # 2. Asegurar canales por defecto (solo DEVESA y AsisTEC)
    area_names = [
        "DEVESA",
        "AsisTEC",
    ]

    additional_channels = (
        db.query(models.Channel)
        .join(models.Area)
        .filter(models.Area.area_name.in_(area_names))
        .all()
    )

    for channel in additional_channels:
        exists = (
            db.query(models.Subscription)
            .filter_by(user_id=db_user.user_id, channel_id=channel.channel_id)
            .first()
        )
        if not exists:
            db.add(
                models.Subscription(
                    user_id=db_user.user_id,
                    channel_id=channel.channel_id,
                    is_admin=False,
                    is_subscribed=True,
                )
            )
        elif not exists.is_subscribed:
            exists.is_subscribed = True


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

    _ensure_primary_subscriptions(new_user, db)

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
    _ensure_primary_subscriptions(db_user, db)
    db.commit()

    admin_subs = (
        db.query(models.Subscription, models.Channel)
        .join(models.Channel, models.Subscription.channel_id == models.Channel.channel_id)
        .filter(models.Subscription.user_id == db_user.user_id, models.Subscription.is_admin == True)
        .all()
    )
    admin_channels = [
        {"channel_id": sub.channel_id, "channel_name": ch.channel_name}
        for sub, ch in admin_subs
    ]

    return {
        "user_id": db_user.user_id,
        "email": db_user.mail,
        "full_name": f"{db_user.name} {db_user.lastname}",
        "area": db_user.area.area_name,
        "area_id": db_user.area_id,
        "user_type": db_user.user_type,
        "is_channel_admin": len(admin_channels) > 0,
        "admin_channels": admin_channels,
        "profile_image": db_user.profile_image,
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


def get_user_next_activities(user_id: str, db: Session):
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


def update_profile_image(user_id: str, profile_image: str, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.profile_image = profile_image
    db.commit()
    return {"msg": "SUCCESS"}


def activate_user(user_id: str, db: Session):
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
