from pydantic import BaseModel, ConfigDict

class MerchantBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    balance: float = 0.0
    user_id: int | None = 0

class CreateMerchant(MerchantBase):
    pass


class UpdateMerchant(MerchantBase):
    pass


class Merchant(MerchantBase):
    id: int


class MerchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchants: list[Merchant]
    page: int
    page_count: int
    size_per_page: int