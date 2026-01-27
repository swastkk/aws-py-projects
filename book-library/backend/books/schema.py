from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BookCreate(BaseModel):
    name: str
    author: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
