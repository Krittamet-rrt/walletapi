from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from models.merchant import Merchant
from models.item import Item
from models.wallet import Wallet
from models.transaction import Transaction

class DBWallet(Wallet, SQLModel, table=True):
    __tablename__ = "wallets"
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: list["DBTransaction"] = Relationship(back_populates="wallet")

class DBMerchant(Merchant, SQLModel, table=True):
    __tablename__ = "merchants"
    id: Optional[int] = Field(default=None, primary_key=True)
    items: list["DBItem"] = Relationship(back_populates="merchant", cascade_delete=True)

class DBItem(Item, SQLModel, table=True):
    __tablename__ = "items"
    id: Optional[int] = Field(default=None, primary_key=True)
    merchant_id: Optional[int] = Field(default=None, foreign_key="merchants.id")
    merchant: Optional[DBMerchant] = Relationship(back_populates="items")
    transactions: list["DBTransaction"] = Relationship(back_populates="item")

class DBTransaction(Transaction, SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_id: int = Field(foreign_key="wallets.id")
    wallet: DBWallet = Relationship(back_populates="transactions")
    item_id: int = Field(foreign_key="items.id")
    item: Optional[DBItem] = Relationship(back_populates="transactions")