from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas


# Obtener canales a los que el usuario está suscrito
def subscribed_channels(user_id: int, db: Session):
    query = db.query(models.Subscription).filter(models.Subscription.user_id == user_id)
    query = query.filter(models.Subscription.is_subscribed == True)

    subscriptions = query.join(models.Channel).all()

    asistec_area = db.query(models.Area).filter_by(area_name="AsisTEC").first()
    asistec_area_id = asistec_area.area_id if asistec_area else None

    return [
        {
            "channel_id": sub.channel.channel_id,
            "channel_name": sub.channel.channel_name,
            "area_id": sub.channel.area_id,
            "is_admin": sub.is_admin,
            "is_subscribed": sub.is_subscribed,
            "is_system": sub.channel.area_id == asistec_area_id,
        }
        for sub in subscriptions
    ]


# Obtener canales disponibles (a los que el usuario no está suscrito actualmente)
# El canal AsisTEC se excluye porque la suscripción es obligatoria.
def not_subscribed_channels(user_id: int, db: Session):
    subscribed_ids = [
        row[0]
        for row in db.query(models.Subscription.channel_id).filter(
            models.Subscription.user_id == user_id,
            models.Subscription.is_subscribed == True,
        ).all()
    ]

    asistec_area = db.query(models.Area).filter_by(area_name="AsisTEC").first()
    asistec_area_id = asistec_area.area_id if asistec_area else None

    all_channels = db.query(models.Channel).all()
    result = []
    for ch in all_channels:
        if ch.channel_id not in subscribed_ids and ch.area_id != asistec_area_id:
            result.append({
                "channel_id": ch.channel_id,
                "channel_name": ch.channel_name,
                "area_id": ch.area_id,
                "is_admin": False,
                "is_subscribed": False,
                "is_system": False,
            })
    return result


# Obtener todos los canales (sin importar suscripción)
def get_all_channels(db: Session):
    channels = db.query(models.Channel).all()
    return [
        {
            "channel_id": ch.channel_id,
            "channel_name": ch.channel_name,
            "area_id": ch.area_id,
        }
        for ch in channels
    ]


# Crear un nuevo canal si no existe uno con el mismo nombre
def create_channel(channel: schemas.ChannelBase, db: Session):
    existing = (
        db.query(models.Channel).filter_by(channel_name=channel.channel_name).first()
    )
    if existing:
        raise HTTPException(
            status_code=409, detail="Channel with this name already exists"
        )

    new_channel = models.Channel(**channel.model_dump())
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    return {"msg": "SUCCESS", "channel_id": new_channel.channel_id}
