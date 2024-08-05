from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from .merchant import MerchantBase
from .item import ItemBase
from .wallet import WalletBase
from .transaction import TransactionBase

class Wallet(WalletBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: list["Transaction"] = Relationship(back_populates="wallet")

class Item(ItemBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    merchant_id: Optional[int] = Field(default=None, foreign_key="merchant.id")
    merchant: Optional["Merchant"] = Relationship(back_populates="items")
    transactions: list["Transaction"] = Relationship(back_populates="item")

class Merchant(MerchantBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: list["Item"] = Relationship(back_populates="merchant", cascade_delete=True)

class Transaction(TransactionBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_id: int = Field(foreign_key="wallet.id")
    wallet: Wallet = Relationship(back_populates="transactions")
    item_id: int = Field(foreign_key="item.id")
    item: Optional[Item] = Relationship(back_populates="transactions")
