from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional

# Professor Schemas
class ProfessorBase(BaseModel):
    professor_name: str
    professor_lastname: str

    @field_validator("professor_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre del profesor no puede estar vacío")
        return v.strip()

    @field_validator("professor_lastname")
    @classmethod
    def lastname_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El apellido del profesor no puede estar vacío")
        return v.strip()

class ProfessorResponse(ProfessorBase):
    professor_id: int
    model_config = ConfigDict(from_attributes=True)

class ProfessorAreaCreate(BaseModel):
    professor_id: int
    area_id: int

class AreaBasic(BaseModel):
    area_id: int
    area_name: str
    model_config = ConfigDict(from_attributes=True)

class ProfessorWithAreas(BaseModel):
    professor_id: int
    professor_name: str
    professor_lastname: str
    areas: List[AreaBasic] = []
