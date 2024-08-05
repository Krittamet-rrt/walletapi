from pydantic import BaseModel

class WalletBase(BaseModel):
    name: str
    balance: float = 0.0