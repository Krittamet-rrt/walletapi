from fastapi import APIRouter, HTTPException, Depends

from models.wallet import Wallet, CreateWallet, UpdateWallet
from models.dbmodels import DBWallet

from typing import Annotated

from sqlmodel.ext.asyncio.session import AsyncSession

import models

router = APIRouter(prefix="/wallets", tags=["Wallet"])

@router.post("",response_model=Wallet)
async def create_wallet(wallet: CreateWallet, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Wallet:
    db_wallet = DBWallet(**wallet.dict())
    await session.add(db_wallet)
    await session.commit()
    session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.get("/{wallet_id}", response_model=Wallet)
async def read_wallet(wallet_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Wallet:
    db_wallet = await session.get(DBWallet, wallet_id)
    if db_wallet:
        return Wallet.from_orm(db_wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("/{wallet_id}", response_model=Wallet)
async def update_wallet(wallet_id: int, wallet: UpdateWallet, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Wallet:
    db_wallet = await session.get(DBWallet, wallet_id)
    if db_wallet:
        for key, value in wallet.dict().items():
            setattr(db_wallet, key, value)
        await session.add(db_wallet)
        await session.commit()
        session.refresh(db_wallet)
        return Wallet.from_orm(db_wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.delete("/{wallet_id}")
async def delete_wallet(wallet_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Wallet:
    db_wallet = await session.get(DBWallet, wallet_id)
    if db_wallet:
        session.delete(db_wallet)
        await session.commit()
        return {"message": "Wallet deleted successfully"}
    raise HTTPException(status_code=404, detail="Wallet not found")