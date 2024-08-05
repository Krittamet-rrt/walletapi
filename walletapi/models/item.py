from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = 0.12
    tax: Optional[float] = None