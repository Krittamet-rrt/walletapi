from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import Session

from models.dbmodels import Wallet, Item, Merchant, Transaction

from models import get_session

router = APIRouter(prefix="/buy_item", tags=["Buy Item"])

@router.post("")
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
    transaction = Transaction(price=item.price, wallet_id=wallet.id, item_id=item.id, description=f"Bought {item.name}")
    
    session.add(wallet)
    session.add(transaction)
    session.commit()
    
    # Fetch merchant information
    merchant = item.merchant

    return {
        "message": f"Successfully bought {item.name}",
        "amount": wallet.balance,
        "item": {"item_id": item.id,"name": item.name, "price": item.price},
        "merchant": {
            "name": merchant.name
        }
    }