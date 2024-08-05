from typing import Optional
from pydantic import BaseModel

class TransactionBase(BaseModel):
    price: float
    wallet_id: int
    description: Optional[str] = None