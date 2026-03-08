from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from datetime import datetime, date
from typing import Optional

# Event Schemas
class EventBase(BaseModel):
    event_title: str
    event_description: str
    event_date: date
    event_start_hour: datetime
    event_final_hour: datetime
    notification_datetime: Optional[str] = None
    all_day: bool

    @field_validator("event_title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El título del evento no puede estar vacío")
        return v.strip()

    @field_validator("event_description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("La descripción del evento no puede estar vacía")
        return v.strip()

    @field_validator("event_date")
    @classmethod
    def date_not_in_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("La fecha del evento no puede ser en el pasado")
        return v

    @model_validator(mode="after")
    def validate_hours(self):
        if self.event_start_hour >= self.event_final_hour:
            raise ValueError("La hora de inicio debe ser antes de la hora de fin")
        if self.event_start_hour.hour < 7:
            raise ValueError("La hora de inicio no puede ser antes de las 7:00 AM")
        if self.event_start_hour.hour >= 23:
            raise ValueError("La hora de inicio no puede ser después de las 11:00 PM")
        if self.event_final_hour.hour < 7:
            raise ValueError("La hora de fin no puede ser antes de las 7:00 AM")
        if self.event_final_hour.hour >= 23:
            raise ValueError("La hora de fin no puede ser después de las 11:00 PM")
        return self

class EventCreate(EventBase):
    user_id: int

class EventResponse(EventBase):
    event_id: int
    model_config = ConfigDict(from_attributes=True)
