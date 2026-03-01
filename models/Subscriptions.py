from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    channel_id = Column(Integer, ForeignKey("channels.channel_id"))
    is_admin = Column(Boolean, default=False)
    is_subscribed = Column(Boolean, default=False)

    user = relationship("User", back_populates="subscriptions")
    channel = relationship("Channel", back_populates="subscriptions")