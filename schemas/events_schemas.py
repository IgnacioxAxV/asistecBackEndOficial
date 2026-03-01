from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional

# Event Schemas
class EventBase(BaseModel):
    event_title: str
    event_description: str
    event_date: datetime
    event_start_hour: datetime
    event_final_hour: datetime
    notification_datetime: Optional[str] = None  # String para formato DD/MM/AAAA HH:MM
    all_day: bool

    @model_validator(mode="after")
    def validate_hours(self):
        if self.event_start_hour >= self.event_final_hour:
            raise ValueError("event_start_hour must be before event_final_hour")
        return self

class EventCreate(EventBase):
    user_id: int

class EventResponse(EventBase):
    event_id: int
    model_config = ConfigDict(from_attributes=True)
