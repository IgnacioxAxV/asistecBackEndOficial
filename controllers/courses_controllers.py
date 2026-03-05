from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models
import schemas
import json


# Obtener cursos asociados a un usuario
def get_user_courses(user_id: int, db: Session):
    courses = db.query(models.Course).filter(models.Course.user_id == user_id).all()

    return [
        {
            "course_id": c.course_id,
            "course_title": c.course_title,
            "course_type": c.course_type,
            "location": c.location,
            "schedule": json.loads(c.schedule),  # ← deserialización
            "course_start_date": c.course_start_date.strftime("%Y-%m-%d"),
            "course_final_date": c.course_final_date.strftime("%Y-%m-%d"),
            "notification_datetime": c.notification_datetime,
            "user_id": c.user_id,
            "professor_id": c.professor_id,
        }
        for c in courses
    ]


# Crear un nuevo curso
def create_course(course: schemas.CourseCreate, db: Session):
    if not db.query(models.User).filter(models.User.user_id == course.user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not db.query(models.Professor).filter(models.Professor.professor_id == course.professor_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor not found")

    new_course = models.Course(**course.to_db_dict())  # ← serializa schedule
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return JSONResponse(
        content={"msg": "SUCCESS", "course_id": new_course.course_id},
        status_code=status.HTTP_201_CREATED,
    )


# Actualizar un curso existente
def update_course(
    course_id: int, course: schemas.CourseCreate, db: Session
):
    db_course = (
        db.query(models.Course).filter(models.Course.course_id == course_id).first()
    )
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    updated_data = course.to_db_dict()  # ← serializa schedule aquí también
    for key, value in updated_data.items():
        setattr(db_course, key, value)

    db.commit()
    db.refresh(db_course)
    return {"msg": "SUCCESS"}


# Eliminar un curso existente
def delete_course(course_id: int, db: Session):
    db_course = (
        db.query(models.Course).filter(models.Course.course_id == course_id).first()
    )
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(db_course)
    db.commit()
    return {"msg": "SUCCESS"}
