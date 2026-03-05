from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    mail = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    carnet_number = Column(String, nullable=False)         # ← Nuevo campo
    gender = Column(String, nullable=False)                # ← Nuevo campo (M/F/otro)
    birth_date = Column(Date, nullable=False)              # ← Nuevo campo
    area_id = Column(Integer, ForeignKey("areas.area_id"))
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)
    user_type = Column(Integer, default=1)

    area = relationship("Area", back_populates="users")
    subscriptions = relationship("Subscription", back_populates="user")
    posts = relationship("Post", back_populates="user")
    events = relationship("Event", back_populates="user")
    courses = relationship("Course", back_populates="user")
    activities = relationship("Activity", back_populates="user")
