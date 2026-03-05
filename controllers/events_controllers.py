from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models
import schemas


def get_user_events(user_id: int, db: Session):
    if not db.query(models.User).filter(models.User.user_id == user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_events = (
        db.query(models.Event)
        .filter(models.Event.user_id == user_id)
        .order_by(models.Event.event_date.asc())
        .all()
    )
    return db_events


def create_event(event: schemas.EventCreate, db: Session):
    if not db.query(models.User).filter(models.User.user_id == event.user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        new_event = models.Event(**event.model_dump())
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return JSONResponse(
        content={"msg": "SUCCESS", "event_id": new_event.event_id},
        status_code=status.HTTP_201_CREATED,
    )


def update_event(
    event_id: int, event: schemas.EventCreate, db: Session
):
    db_event = db.query(models.Event).filter(models.Event.event_id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    for key, value in event.model_dump().items():
        setattr(db_event, key, value)

    db.commit()
    db.refresh(db_event)
    return {"msg": "SUCCESS"}


def delete_event_by_id(event_id: int, db: Session):
    db_event = db.query(models.Event).filter(models.Event.event_id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    db.delete(db_event)
    db.commit()

    return JSONResponse(content={"msg": "SUCCESS"}, status_code=status.HTTP_200_OK)
