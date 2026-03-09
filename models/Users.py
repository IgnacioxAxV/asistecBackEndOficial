import uuid
import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    mail = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    carnet_number = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    area_id = Column(String(36), ForeignKey("areas.area_id"))
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)
    user_type = Column(String, default="1")
    profile_image = Column(String, nullable=True)

    area = relationship("Area", back_populates="users")
    subscriptions = relationship("Subscription", back_populates="user")
    posts = relationship("Post", back_populates="user")
    events = relationship("Event", back_populates="user")
    courses = relationship("Course", back_populates="user")
    activities = relationship("Activity", back_populates="user")
