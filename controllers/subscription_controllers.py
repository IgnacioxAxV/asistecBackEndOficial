from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models
import schemas


# Crear una nueva suscripción
def create_subscription(
    subscription: schemas.SubscriptionBase, db: Session
):
    # Verificamos si el usuario ya está suscrito al canal
    existing = (
        db.query(models.Subscription)
        .filter_by(user_id=subscription.user_id, channel_id=subscription.channel_id)
        .first()
    )

    if existing:
        # Si la suscripción existe, verificamos si el estado de is_subscribed es diferente
        if existing.is_subscribed != subscription.is_subscribed:
            # Si es diferente, actualizamos el estado de is_subscribed
            existing.is_subscribed = subscription.is_subscribed
            db.commit()
            db.refresh(existing)
            return JSONResponse(
                content={
                    "msg": "Subscription updated",
                    "subscription_id": existing.subscription_id,
                },
                status_code=status.HTTP_200_OK,
            )
        # Si el estado es el mismo, no hacemos nada
        raise HTTPException(
            status_code=409, detail="User already subscribed with same favorite status"
        )

    # Si no existe la suscripción, creamos una nueva
    new_sub = models.Subscription(**subscription.model_dump())
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return JSONResponse(
        content={"msg": "SUCCESS", "subscription_id": new_sub.subscription_id},
        status_code=status.HTTP_201_CREATED,
    )


# Cancelar una suscripción existente (marca is_subscribed=False)
def cancel_subscription(user_id: int, channel_id: int, db: Session):
    subscription = (
        db.query(models.Subscription)
        .filter_by(user_id=user_id, channel_id=channel_id)
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
        )

    channel = db.query(models.Channel).filter_by(channel_id=channel_id).first()
    user = db.query(models.User).filter_by(user_id=user_id).first()

    if channel and user and channel.area_id == user.area_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes desuscribirte del canal de tu carrera",
        )

    subscription.is_subscribed = False
    db.commit()

    return JSONResponse(content={"msg": "SUCCESS"}, status_code=status.HTTP_200_OK)


# Asignar privilegios de administrador a una suscripción existente
def make_admin(user_id: int, channel_id: int, db: Session):
    # Buscar la suscripción correspondiente
    subscription = (
        db.query(models.Subscription)
        .filter_by(user_id=user_id, channel_id=channel_id)
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
        )

    # Actualizar el campo is_admin a True
    subscription.is_admin = True
    db.commit()
    db.refresh(subscription)

    return JSONResponse(
        content={
            "msg": "SUCCESS - User promoted to admin",
            "subscription_id": subscription.subscription_id,
        },
        status_code=status.HTTP_200_OK,
    )
