from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Post Schemas
class PostCreate(BaseModel):
    channel_id: int
    user_id: int
    title: str
    content: str
    tags: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None

class PostResponse(BaseModel):
    post_id: int
    channel_id: int
    channel_name: Optional[str] = None
    user_id: int
    title: str
    content: str
    tags: Optional[str] = None
    date: datetime

    model_config = ConfigDict(from_attributes=True)
