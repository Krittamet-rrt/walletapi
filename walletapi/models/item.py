from pydantic import BaseModel, ConfigDict
from typing import Optional


class ItemBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    price: float = 0.12
    tax: Optional[float] = None

class CreateItem(ItemBase):
    pass

class UpdateItem(ItemBase):
    pass

class Item(ItemBase):
    id: int

class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Item]
    page: int
    page_size: int
    size_per_page: int