from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel.ext.asyncio.session import AsyncSession

from models.dbmodels import DBWallet, DBItem, DBMerchant, DBTransaction

import models

router = APIRouter(prefix="/buy_item", tags=["Buy Item"])

@router.post("")
async def buy_item(item_id: int, wallet_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]):
    item = await session.get(DBItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    wallet = session.get(DBWallet, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.balance < item.price:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    merchant = session.get(DBMerchant, item.merchant_id)

    wallet.balance -= item.price
    merchant.balance += item.price
    
    transaction = DBTransaction(price=item.price, wallet_id=wallet.id, item_id=item.id, description=f"Bought {item.name}")
    
    session.add(wallet)
    session.add(transaction)
    session.commit()
    
    merchant = item.merchant

    return {
        "message": f"Successfully bought {item.name}",
        "amount": wallet.balance,
        "item": {"item_id": item.id,"name": item.name, "price": item.price},
        "merchant": {
            "name": merchant.name
        }
    }