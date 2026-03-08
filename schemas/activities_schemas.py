from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from datetime import date
from typing import Optional, Dict
import json
import re

VALID_DAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
TIME_PATTERN = re.compile(r"^\d{2}:\d{2}$")

# Activity Schemas
class ActivityBase(BaseModel):
    activity_title: str
    location: str
    schedule: Dict[str, Dict[str, str]]
    activity_start_date: date
    activity_final_date: date
    notification_datetime: Optional[str] = None

    @field_validator("activity_title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El título de la actividad no puede estar vacío")
        return v.strip()

    @field_validator("location")
    @classmethod
    def location_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("La ubicación no puede estar vacía")
        return v.strip()

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
        if not v:
            raise ValueError("El horario no puede estar vacío")
        for key, entry in v.items():
            if "date" not in entry:
                raise ValueError(f"La entrada '{key}' del schedule debe incluir el campo 'date'")
            if entry["date"].lower() not in VALID_DAYS:
                raise ValueError(f"El día '{entry['date']}' no es válido. Debe ser un día de la semana en inglés")
            if "start_time" not in entry:
                raise ValueError(f"La entrada '{key}' del schedule debe incluir el campo 'start_time'")
            if not TIME_PATTERN.match(entry["start_time"]):
                raise ValueError(f"El formato de start_time '{entry['start_time']}' no es válido. Use HH:MM")
            start_hour = int(entry["start_time"].split(":")[0])
            if start_hour < 7:
                raise ValueError(f"La hora de inicio no puede ser antes de las 7:00 AM")
            if start_hour >= 23:
                raise ValueError(f"La hora de inicio no puede ser después de las 11:00 PM")
            if "end_time" in entry and TIME_PATTERN.match(entry["end_time"]):
                end_hour = int(entry["end_time"].split(":")[0])
                end_min = int(entry["end_time"].split(":")[1])
                if end_hour < 7:
                    raise ValueError(f"La hora de fin no puede ser antes de las 7:00 AM")
                if end_hour >= 23:
                    raise ValueError(f"La hora de fin no puede ser después de las 11:00 PM")
                start_total = start_hour * 60 + int(entry["start_time"].split(":")[1])
                end_total = end_hour * 60 + end_min
                if start_total >= end_total:
                    raise ValueError(f"La hora de inicio ({entry['start_time']}) debe ser menor que la hora de fin ({entry['end_time']})")
        return v

    @model_validator(mode="after")
    def validate_dates(self):
        if self.activity_start_date > self.activity_final_date:
            raise ValueError("La fecha de inicio debe ser antes de la fecha final")
        return self

    def to_db_dict(self):
        data = self.model_dump()
        data["schedule"] = json.dumps(self.schedule)
        return data

class ActivityCreate(ActivityBase):
    user_id: int

class ActivityResponse(ActivityBase):
    activity_id: int
    model_config = ConfigDict(from_attributes=True)

