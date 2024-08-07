from pydantic import BaseModel, ConfigDict

class WalletBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    balance: float = 0.0

class CreateWallet(WalletBase):
    pass

class UpdateWallet(WalletBase):
    pass

class Wallet(WalletBase):
    id: int