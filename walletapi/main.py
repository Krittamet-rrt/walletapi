from fastapi import FastAPI, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship

# Define the Wallet model
class WalletBase(BaseModel):
    name: str
    balance: float = 0.0

class Wallet(WalletBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: list["Transaction"] = Relationship(back_populates="wallet")

# Define the Merchant model
class MerchantBase(BaseModel):
    name: str
    balance: float = 0.0

class Merchant(MerchantBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: list["Item"] = Relationship(back_populates="merchant")

# Define the Item model
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = 0.12
    tax: Optional[float] = None

class Item(ItemBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    merchant_id: Optional[int] = Field(default=None, foreign_key="merchant.id")
    merchant: Optional[Merchant] = Relationship(back_populates="items")

# Define the Transaction model
class TransactionBase(BaseModel):
    price: float
    wallet_id: int
    description: Optional[str] = None

class Transaction(TransactionBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_id: int = Field(foreign_key="wallet.id")
    wallet: Wallet = Relationship(back_populates="transactions")


connect_args = {}

engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/walletdb",
    echo=True,
    connect_args=connect_args,
)

# SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

app = FastAPI()

def get_session():
    with Session(engine) as session:
        yield session

# Wallet CRUD operations
@app.post("/wallets/", response_model=Wallet, tags=["Wallet"])
async def create_wallet(wallet: WalletBase, session: Session = Depends(get_session)):
    db_wallet = Wallet(**wallet.dict())
    session.add(db_wallet)
    session.commit()
    session.refresh(db_wallet)
    return db_wallet

@app.get("/wallets/", response_model=list[Wallet], tags=["Wallet"])
async def read_wallets(session: Session = Depends(get_session)):
    return session.exec(select(Wallet)).all()

@app.get("/wallets/{wallet_id}", response_model=Wallet, tags=["Wallet"])
async def read_wallet(wallet_id: int, session: Session = Depends(get_session)):
    db_wallet = session.get(Wallet, wallet_id)
    if db_wallet:
        return db_wallet
    raise HTTPException(status_code=404, detail="Wallet not found")

@app.put("/wallets/{wallet_id}", response_model=Wallet, tags=["Wallet"])
async def update_wallet(wallet_id: int, wallet: WalletBase, session: Session = Depends(get_session)):
    db_wallet = session.get(Wallet, wallet_id)
    if db_wallet:
        for key, value in wallet.dict().items():
            setattr(db_wallet, key, value)
        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)
        return db_wallet
    raise HTTPException(status_code=404, detail="Wallet not found")

@app.delete("/wallets/{wallet_id}", tags=["Wallet"])
async def delete_wallet(wallet_id: int, session: Session = Depends(get_session)):
    db_wallet = session.get(Wallet, wallet_id)
    if db_wallet:
        session.delete(db_wallet)
        session.commit()
        return {"message": "Wallet deleted successfully"}
    raise HTTPException(status_code=404, detail="Wallet not found")

# Merchant CRUD operations
@app.post("/merchants/", response_model=Merchant, tags=["Merchant"])
async def create_merchant(merchant: MerchantBase, session: Session = Depends(get_session)):
    db_merchant = Merchant(**merchant.dict())
    session.add(db_merchant)
    session.commit()
    session.refresh(db_merchant)
    return db_merchant

@app.get("/merchants/", response_model=list[Merchant], tags=["Merchant"])
async def read_merchants(session: Session = Depends(get_session)):
    return session.exec(select(Merchant)).all()

@app.get("/merchants/{merchant_id}", response_model=Merchant, tags=["Merchant"])
async def read_merchant(merchant_id: int, session: Session = Depends(get_session)):
    db_merchant = session.get(Merchant, merchant_id)
    if db_merchant:
        return db_merchant
    raise HTTPException(status_code=404, detail="Merchant not found")

@app.put("/merchants/{merchant_id}", response_model=Merchant, tags=["Merchant"])
async def update_merchant(merchant_id: int, merchant: MerchantBase, session: Session = Depends(get_session)):
    db_merchant = session.get(Merchant, merchant_id)
    if db_merchant:
        for key, value in merchant.dict().items():
            setattr(db_merchant, key, value)
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)
        return db_merchant
    raise HTTPException(status_code=404, detail="Merchant not found")

@app.delete("/merchants/{merchant_id}", tags=["Merchant"])
async def delete_merchant(merchant_id: int, session: Session = Depends(get_session)):
    db_merchant = session.get(Merchant, merchant_id)
    if db_merchant:
        session.delete(db_merchant)
        session.commit()
        return {"message": "Merchant deleted successfully"}
    raise HTTPException(status_code=404, detail="Merchant not found")

# Item CRUD operations

@app.get("/items/", response_model=list[Item], tags=["Item"])
async def read_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()

@app.post("/items/{merchant_id}", response_model=Item, tags=["Item"])
async def create_item(merchant_id: int, item: ItemBase, session: Session = Depends(get_session)):
    db_item = Item(**item.dict())
    Item.merchant_id = merchant_id
    if Item.merchant_id:
        merchant = session.get(Merchant, Item.merchant_id)
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        db_item.merchant = merchant
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@app.get("/items/{item_id}", response_model=Item, tags=["Item"])
async def read_item(item_id: int, session: Session = Depends(get_session)):
    db_item = session.get(Item, item_id)
    if db_item:
        return db_item
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}", response_model=Item, tags=["Item"])
async def update_item(item_id: int, item: ItemBase, session: Session = Depends(get_session)):
    db_item = session.get(Item, item_id)
    if db_item:
        for key, value in item.dict().items():
            setattr(db_item, key, value)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}", tags=["Item"])
async def delete_item(item_id: int, session: Session = Depends(get_session)):
    db_item = session.get(Item, item_id)
    if db_item:
        session.delete(db_item)
        session.commit()
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/buy-item/", tags=["Buy Item"])
async def buy_item(item_id: int, wallet_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    wallet = session.get(Wallet, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.balance < item.price:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    merchant = session.get(Merchant, item.merchant_id)

    # Update wallet balance
    wallet.balance -= item.price
    merchant.balance += item.price
    
    # Create transaction
    transaction = Transaction(price=item.price, wallet_id=wallet.id, description=f"Bought {item.name}")
    
    session.add(wallet)
    session.add(transaction)
    session.commit()
    
    # Fetch merchant information
    merchant = item.merchant

    return {
        "message": f"Successfully bought {item.name}",
        "amount": wallet.balance,
        "item": item,
        "merchant": {
            "id": merchant.id,
            "name": merchant.name
        }
    }

@app.get("/transactions/", response_model=list[Transaction], tags=["Transaction"])
async def read_transactions(session: Session = Depends(get_session)):
    return session.exec(select(Transaction)).all()

@app.get("/transactions/{transaction_id}", response_model=Transaction, tags=["Transaction"])
async def read_transaction(transaction_id: int, session: Session = Depends(get_session)):
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction:
        return db_transaction
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.put("/transactions/{transaction_id}", response_model=Transaction, tags=["Transaction"])
async def update_transaction(transaction_id: int, transaction: TransactionBase, session: Session = Depends(get_session)):
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction:
        for key, value in transaction.dict().items():
            setattr(db_transaction, key, value)
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)
        return db_transaction
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.delete("/transactions/{transaction_id}", tags=["Transaction"])
async def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction:
        session.delete(db_transaction)
        session.commit()
        return {"message": "Transaction deleted successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found")