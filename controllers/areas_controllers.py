from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas


# Obtener todas las áreas (area_id siempre como string para el schema)
def get_areas(db: Session):
    areas = db.query(models.Area).all()
    return [
        {"area_id": str(a.area_id), "area_name": a.area_name, "is_major": a.is_major}
        for a in areas
    ]


# Crear una nueva área y su canal asociado automáticamente
def create_area(area: schemas.AreaBase, db: Session):
    existing = db.query(models.Area).filter_by(area_name=area.area_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Area with this name already exists",
        )

    new_area = models.Area(**area.model_dump())
    db.add(new_area)
    db.commit()
    db.refresh(new_area)

    # Crear canal asociado
    new_channel = models.Channel(
        channel_name=f"Canal de {new_area.area_name}", area_id=new_area.area_id
    )
    db.add(new_channel)
    db.commit()

    return {"msg": "SUCCESS", "area_id": new_area.area_id, "channel_id": new_channel.channel_id}


# Obtener las áreas donde el is_major sea True (area_id siempre como string)
def get_major_areas(db: Session):
    areas = db.query(models.Area).filter_by(is_major=True).all()
    return [
        {"area_id": str(a.area_id), "area_name": a.area_name, "is_major": a.is_major}
        for a in areas
    ]
