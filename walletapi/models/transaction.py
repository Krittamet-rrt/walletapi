from typing import Optional
from pydantic import BaseModel, ConfigDict

class TransactionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    price: float
    wallet_id: int
    description: Optional[str] = None

class CreateTransaction(TransactionBase):
    pass


class UpdateTransaction(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: int

class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    transactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int