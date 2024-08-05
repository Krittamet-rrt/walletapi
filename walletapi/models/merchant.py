from pydantic import BaseModel

class MerchantBase(BaseModel):
    name: str
    balance: float = 0.0