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
    # date se omite — el modelo la asigna automáticamente (default=datetime.utcnow)

class PostResponse(BaseModel):
    post_id: int
    channel_id: int
    user_id: int
    title: str
    content: str
    tags: Optional[str] = None
    date: datetime  # Pydantic serializa a ISO 8601; el frontend parsea con new Date()

    model_config = ConfigDict(from_attributes=True)
