from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import schemas
from database import get_db
from controllers.professors_controllers import (
    create_professor,
    get_all_professors,
    assign_professor_area,
    remove_professor_area,
)

professor_router = APIRouter(prefix="/api/professors", tags=["Professors"])


@professor_router.get("/", response_model=list[schemas.ProfessorWithAreas])
def get_all_professors_route(
    area_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return get_all_professors(db, area_id)


@professor_router.post("/create", status_code=status.HTTP_201_CREATED)
def create_professor_route(
    professor: schemas.ProfessorBase, db: Session = Depends(get_db)
):
    return create_professor(professor, db)


@professor_router.post("/assign_area", status_code=status.HTTP_201_CREATED)
def assign_professor_area_route(
    data: schemas.ProfessorAreaCreate, db: Session = Depends(get_db)
):
    return assign_professor_area(data, db)


@professor_router.delete("/remove_area")
def remove_professor_area_route(
    professor_id: int, area_id: int, db: Session = Depends(get_db)
):
    return remove_professor_area(professor_id, area_id, db)
