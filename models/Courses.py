from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_title = Column(String, nullable=False)
    course_type = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    schedule = Column(String)  # JSON field
    course_start_date = Column(DateTime, nullable=False)
    course_final_date = Column(DateTime, nullable=False)
    notification_datetime = Column(String)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    professor_name = Column(String, nullable=False)

    user = relationship("User", back_populates="courses")