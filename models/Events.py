from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    event_title = Column(String, nullable=False)
    event_description = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    event_start_hour = Column(DateTime, nullable=False)
    event_final_hour = Column(DateTime, nullable=False)
    notification_datetime = Column(String)  # Podría ser un Enum
    all_day = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    user = relationship("User", back_populates="events")