import uuid

from pydantic import BaseModel, Field


class ResponseMedia(BaseModel):
    media_id: uuid.UUID = Field(..., examples=[uuid.uuid4()])

    class Config:
        from_attributes = True
