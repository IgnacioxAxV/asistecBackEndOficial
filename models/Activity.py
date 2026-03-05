from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True, index=True)
    activity_title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    schedule = Column(String)  # JSON field
    activity_start_date = Column(DateTime, nullable=False)
    activity_final_date = Column(DateTime, nullable=False)
    notification_datetime = Column(String)  # Podría ser un Enum
    user_id = Column(Integer, ForeignKey("users.user_id"))

    user = relationship("User", back_populates="activities")