from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import models
import schemas


def get_all_professors(db: Session, area_id: Optional[int] = None):
    if area_id is not None:
        area = db.query(models.Area).filter(models.Area.area_id == area_id).first()
        if not area:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found")

        professor_ids = (
            db.query(models.ProfessorArea.professor_id)
            .filter(models.ProfessorArea.area_id == area_id)
            .all()
        )
        ids = [pid[0] for pid in professor_ids]
        professors = db.query(models.Professor).filter(models.Professor.professor_id.in_(ids)).all()
    else:
        professors = db.query(models.Professor).all()

    result = []
    for prof in professors:
        areas = (
            db.query(models.Area)
            .join(models.ProfessorArea, models.Area.area_id == models.ProfessorArea.area_id)
            .filter(models.ProfessorArea.professor_id == prof.professor_id)
            .all()
        )
        result.append({
            "professor_id": prof.professor_id,
            "professor_name": prof.professor_name,
            "professor_lastname": prof.professor_lastname,
            "areas": [{"area_id": a.area_id, "area_name": a.area_name} for a in areas],
        })
    return result


def create_professor(professor: schemas.ProfessorBase, db: Session):
    new_prof = models.Professor(**professor.model_dump())
    db.add(new_prof)
    db.commit()
    db.refresh(new_prof)
    return {"msg": "SUCCESS", "professor_id": new_prof.professor_id}


def assign_professor_area(data: schemas.ProfessorAreaCreate, db: Session):
    professor = db.query(models.Professor).filter(
        models.Professor.professor_id == data.professor_id
    ).first()
    if not professor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor not found")

    area = db.query(models.Area).filter(models.Area.area_id == data.area_id).first()
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found")

    existing = db.query(models.ProfessorArea).filter(
        models.ProfessorArea.professor_id == data.professor_id,
        models.ProfessorArea.area_id == data.area_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El profesor ya está asignado a esta área",
        )

    new_pa = models.ProfessorArea(professor_id=data.professor_id, area_id=data.area_id)
    db.add(new_pa)
    db.commit()
    return {"msg": "SUCCESS"}


def remove_professor_area(professor_id: int, area_id: int, db: Session):
    record = db.query(models.ProfessorArea).filter(
        models.ProfessorArea.professor_id == professor_id,
        models.ProfessorArea.area_id == area_id,
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El profesor no está asignado a esta área",
        )

    db.delete(record)
    db.commit()
    return {"msg": "SUCCESS"}
