from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models
import schemas


def get_all_professors(db: Session):
    professors = db.query(models.Professor).all()
    return professors


# Crear un nuevo profesor
def create_professor(professor: schemas.ProfessorBase, db: Session):
    new_prof = models.Professor(**professor.model_dump())
    db.add(new_prof)
    db.commit()
    db.refresh(new_prof)
    return JSONResponse(
        content={"msg": "SUCCESS", "professor_id": new_prof.professor_id},
        status_code=status.HTTP_201_CREATED,
    )
