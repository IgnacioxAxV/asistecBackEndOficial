from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Professor(Base):
    __tablename__ = "professors"

    professor_id = Column(Integer, primary_key=True, index=True)
    professor_name = Column(String, nullable=False)
    professor_lastname = Column(String, nullable=False)

    professor_areas = relationship("ProfessorArea", back_populates="professor")
