from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas
import models
from database import get_db
from datetime import datetime
import json


# Obtener las actividades asociadas a un usuario
def get_user_activities(user_id: int, db: Session = Depends(get_db)):
    activities = (
        db.query(models.Activity).filter(models.Activity.user_id == user_id).all()
    )

    return [
        {
            "activity_id": act.activity_id,
            "activity_title": act.activity_title,
            "location": act.location,
            "schedule": json.loads(act.schedule),
            "activity_start_date": act.activity_start_date,
            "activity_final_date": act.activity_final_date,
            "notification_datetime": act.notification_datetime,
        }
        for act in activities
    ]


# Crear una nueva actividad
def create_activity(activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    new_activity = models.Activity(**activity.to_db_dict())
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return {"msg": "SUCCESS", "activity_id": new_activity.activity_id}


# Actualizar una actividad existente
def update_activity(
    activity_id: int, activity: schemas.ActivityCreate, db: Session = Depends(get_db)
):
    db_activity = (
        db.query(models.Activity)
        .filter(models.Activity.activity_id == activity_id)
        .first()
    )
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    updated_data = activity.to_db_dict()  # Serializa schedule aquí
    for key, value in updated_data.items():
        setattr(db_activity, key, value)

    db.commit()
    db.refresh(db_activity)
    return {"msg": "SUCCESS"}


# Eliminar una actividad existente
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = (
        db.query(models.Activity)
        .filter(models.Activity.activity_id == activity_id)
        .first()
    )
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    db.delete(db_activity)
    db.commit()
    return {"msg": "SUCCESS"}
