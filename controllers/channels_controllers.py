from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db


# Obtener canales a los que el usuario está suscrito
def subscribed_channels(user_id: int, db: Session = Depends(get_db)):
    query = db.query(models.Subscription).filter(models.Subscription.user_id == user_id)
    query = query.filter(models.Subscription.is_subscribed == True)

    subscriptions = query.join(models.Channel).all()

    return [
        {
            "channel_id": sub.channel.channel_id,
            "channel_name": sub.channel.channel_name,
            "area_id": sub.channel.area_id,
            "is_admin": sub.is_admin,
            "is_subscribed": sub.is_subscribed,
        }
        for sub in subscriptions
    ]


# Obtener canales a los que el usuario NO está suscrito
def not_subscribed_channels(user_id: int, db: Session = Depends(get_db)):
    query = db.query(models.Subscription).filter(models.Subscription.user_id == user_id)

    query = query.filter(models.Subscription.is_subscribed == False)

    subscriptions = query.join(models.Channel).all()
    return [
        {
            "channel_id": sub.channel.channel_id,
            "channel_name": sub.channel.channel_name,
            "area_id": sub.channel.area_id,
            "is_admin": sub.is_admin,
            "is_subscribed": sub.is_subscribed,
        }
        for sub in subscriptions
    ]


# Obtener todos los canales (sin importar suscripción)
def get_all_channels(db: Session = Depends(get_db)):
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
def create_channel(channel: schemas.ChannelBase, db: Session = Depends(get_db)):
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
