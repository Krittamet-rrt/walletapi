from typing import Optional

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime

from .merchant import MerchantBase
from .item import ItemBase
from .wallet import WalletBase
from .transaction import TransactionBase
from .user import UserBase

import datetime

import bcrypt

# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DBUser(UserBase, SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)

    password: str

    register_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    last_login_date: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True))

    async def has_roles(self, roles):
        for role in roles:
            if role in self.roles:
                return True
        return False

    async def get_encrypted_password(self, plain_password):
        return bcrypt.hashpw(
            plain_password.encode("utf-8"), salt=bcrypt.gensalt()
        ).decode("utf-8")

    async def set_password(self, plain_password):
        self.password = await self.get_encrypted_password(plain_password)

    async def verify_password(self, plain_password):
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password.encode("utf-8")
        )
    
class DBWallet(WalletBase, SQLModel, table=True):
    __tablename__ = "wallets"
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: list["DBTransaction"] = Relationship(back_populates="wallet")

class DBMerchant(MerchantBase, SQLModel, table=True):
    __tablename__ = "merchants"
    id: Optional[int] = Field(default=None, primary_key=True)
    items: list["DBItem"] = Relationship(back_populates="merchant", cascade_delete=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    user: DBUser | None = Relationship()

class DBItem(ItemBase, SQLModel, table=True):
    __tablename__ = "items"
    id: Optional[int] = Field(default=None, primary_key=True)
    merchant_id: Optional[int] = Field(default=None, foreign_key="merchants.id")
    merchant: Optional[DBMerchant] = Relationship(back_populates="items")
    transactions: list["DBTransaction"] = Relationship(back_populates="item")
    user_id: int = Field(default=None, foreign_key="users.id")
    user: DBUser | None = Relationship()

class DBTransaction(TransactionBase, SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_id: int = Field(foreign_key="wallets.id")
    wallet: DBWallet = Relationship(back_populates="transactions")
    item_id: int = Field(foreign_key="items.id")
    item: Optional[DBItem] = Relationship(back_populates="transactions")
    transaction_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
