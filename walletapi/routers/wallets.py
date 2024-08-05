from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import Session, select
from models.wallet import WalletBase
from models.dbmodels import Wallet

from models import get_session

router = APIRouter(prefix="/wallets", tags=["Wallet"])

@router.post("",response_model=Wallet)
async def create_wallet(wallet: WalletBase, session: Session = Depends(get_session)):
    db_wallet = Wallet(**wallet.dict())
    session.add(db_wallet)
    session.commit()
    session.refresh(db_wallet)
    return db_wallet

@router.get("",response_model=list[Wallet])
async def read_wallets(session: Session = Depends(get_session)):
    return session.exec(select(Wallet)).all()

@router.get("/{wallet_id}", response_model=Wallet)
async def read_wallet(wallet_id: int, session: Session = Depends(get_session)):
    db_wallet = session.get(Wallet, wallet_id)
    if db_wallet:
        return db_wallet
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("/{wallet_id}", response_model=Wallet)
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

@router.delete("/{wallet_id}")
async def delete_wallet(wallet_id: int, session: Session = Depends(get_session)):
    db_wallet = session.get(Wallet, wallet_id)
    if db_wallet:
        session.delete(db_wallet)
        session.commit()
        return {"message": "Wallet deleted successfully"}
    raise HTTPException(status_code=404, detail="Wallet not found")