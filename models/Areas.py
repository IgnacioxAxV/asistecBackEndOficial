from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Area(Base):
    __tablename__ = "areas"

    area_id = Column(Integer, primary_key=True, index=True)
    area_name = Column(String, nullable=False, unique=True)
    is_major = Column(Boolean, default=False)

    users = relationship("User", back_populates="area")
    channels = relationship("Channel", back_populates="area")
    professor_areas = relationship("ProfessorArea", back_populates="area")