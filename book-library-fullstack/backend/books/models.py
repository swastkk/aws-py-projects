import uuid
from typing import Optional

from pydantic import BaseModel


class BookOut(BaseModel):
    id: uuid.UUID
    name: str
    author: str
    price: float
    image: Optional[str] = None

    class Config:
        from_attributes = True


class BookGET(BaseModel):
    id: uuid.UUID
    name: str
    author: str
    price: float
    image: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
