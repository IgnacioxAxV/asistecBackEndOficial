from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import date

MIN_AGE = 17
MAX_AGE = 70

class UserBase(BaseModel):
    name: str
    lastname: str
    mail: EmailStr
    area_id: str
    carnet_number: str
    gender: str
    birth_date: date

    @field_validator("birth_date")
    @classmethod
    def validate_birth_year(cls, v: date) -> date:
        current_year = date.today().year
        min_year = current_year - MAX_AGE
        max_year = current_year - MIN_AGE

        if v.year > max_year:
            raise ValueError(f"El año de nacimiento no puede ser mayor a {max_year}")
        if v.year < min_year:
            raise ValueError(f"El año de nacimiento no puede ser menor a {min_year}")
        return v

class UserLogin(BaseModel):
    mail: EmailStr
    password: str

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

class ProfileImageUpdate(BaseModel):
    profile_image: str

class UserListResponse(BaseModel):
    user_id: str
    name: str
    lastname: str
    mail: str
    carnet_number: str
    gender: str
    birth_date: date
    area_id: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
