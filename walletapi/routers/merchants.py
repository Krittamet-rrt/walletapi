from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import Session, select
from models.merchant import MerchantBase
from models.dbmodels import Merchant

from models import get_session

router = APIRouter(prefix="/merchants", tags=["Merchant"])

@router.post("",response_model=Merchant)
async def create_merchant(merchant: MerchantBase, session: Session = Depends(get_session)):
    db_merchant = Merchant(**merchant.dict())
    session.add(db_merchant)
    session.commit()
    session.refresh(db_merchant)
    return db_merchant

@router.get("",response_model=list[Merchant])
async def read_merchants(session: Session = Depends(get_session)):
    return session.exec(select(Merchant)).all()

@router.get("/{merchant_id}", response_model=Merchant)
async def read_merchant(merchant_id: int, session: Session = Depends(get_session)):
    db_merchant = session.get(Merchant, merchant_id)
    if db_merchant:
        return db_merchant
    raise HTTPException(status_code=404, detail="Merchant not found")

@router.put("/{merchant_id}", response_model=Merchant)
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

@router.delete("/{merchant_id}")
async def delete_merchant(merchant_id: int, session: Session = Depends(get_session)):
    db_merchant = session.get(Merchant, merchant_id)
    if db_merchant:
        session.delete(db_merchant)
        session.commit()
        return {"message": "Merchant and item deleted successfully"}
    raise HTTPException(status_code=404, detail="Merchant not found")