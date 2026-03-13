import uuid
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    activity_title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    schedule = Column(String)
    activity_start_date = Column(Date, nullable=False)
    activity_final_date = Column(Date, nullable=False)
    notification_datetime = Column(String)
    user_id = Column(String(36), ForeignKey("users.user_id"))

    user = relationship("User", back_populates="activities")
