from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
import json


def _time_to_minutes(t: str) -> int:
    parts = t.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def _check_schedule_overlap(new_schedule: dict, existing_courses, exclude_course_id: int = None):
    """Verifica si el horario del nuevo curso se solapa con cursos existentes."""
    new_entries = []
    for entry in new_schedule.values():
        day = entry["date"].lower()
        start = _time_to_minutes(entry["start_time"])
        end = _time_to_minutes(entry.get("end_time", entry["start_time"]))
        if end <= start:
            end = start + 60
        new_entries.append({"day": day, "start": start, "end": end})

    for course in existing_courses:
        if exclude_course_id and course.course_id == exclude_course_id:
            continue

        existing_schedule = json.loads(course.schedule)
        for ex_entry in existing_schedule.values():
            ex_day = ex_entry["date"].lower()
            ex_start = _time_to_minutes(ex_entry["start_time"])
            ex_end = _time_to_minutes(ex_entry.get("end_time", ex_entry["start_time"]))
            if ex_end <= ex_start:
                ex_end = ex_start + 60

            for new_e in new_entries:
                if new_e["day"] == ex_day and new_e["start"] < ex_end and ex_start < new_e["end"]:
                    day_names = {
                        "monday": "Lunes", "tuesday": "Martes", "wednesday": "Miércoles",
                        "thursday": "Jueves", "friday": "Viernes", "saturday": "Sábado", "sunday": "Domingo",
                    }
                    day_label = day_names.get(new_e["day"], new_e["day"])
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El horario se solapa con el curso '{course.course_title}' el día {day_label}.",
                    )


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
            "professor_name": c.professor_name,
        }
        for c in courses
    ]


# Crear un nuevo curso
def create_course(course: schemas.CourseCreate, db: Session):
    if not db.query(models.User).filter(models.User.user_id == course.user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing_courses = db.query(models.Course).filter(models.Course.user_id == course.user_id).all()
    _check_schedule_overlap(course.schedule, existing_courses)

    new_course = models.Course(**course.to_db_dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return {"msg": "SUCCESS", "course_id": new_course.course_id}


# Actualizar un curso existente
def update_course(
    course_id: int, course: schemas.CourseCreate, db: Session
):
    db_course = (
        db.query(models.Course).filter(models.Course.course_id == course_id).first()
    )
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing_courses = db.query(models.Course).filter(models.Course.user_id == course.user_id).all()
    _check_schedule_overlap(course.schedule, existing_courses, exclude_course_id=course_id)

    updated_data = course.to_db_dict()
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
