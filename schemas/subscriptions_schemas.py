from pydantic import BaseModel, ConfigDict

# Subscription Schemas
class SubscriptionBase(BaseModel):
    user_id: int
    channel_id: int
    is_admin: bool
    is_subscribed: bool

class SubscriptionResponse(SubscriptionBase):
    subscription_id: int
    model_config = ConfigDict(from_attributes=True)
