from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import select
from models.merchant import Merchant, CreateMerchant, UpdateMerchant, MerchantList
from models.dbmodels import DBMerchant

from typing import Annotated

from sqlmodel import select

from sqlmodel.ext.asyncio.session import AsyncSession

import models

router = APIRouter(prefix="/merchants", tags=["Merchant"])


@router.get("",response_model=list[Merchant])
async def read_merchants(session: Annotated[AsyncSession, Depends(models.get_session)], page: int = 1, page_size: int = 10,) -> MerchantList:
    result = await session.exec(
        select(DBMerchant).offset((page - 1) * page_size).limit(page_size)
    )
    db_merchants = result.all()
    return MerchantList(
        merchants=db_merchants,
        page=page,
        page_size=page_size,
        size_per_page=len(db_merchants),
    )

@router.post("", response_model=Merchant)
async def create_merchant(merchant: CreateMerchant, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Merchant:
    db_merchant = DBMerchant(**merchant.dict())
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)
    return Merchant.from_orm(db_merchant)

@router.get("/{merchant_id}", response_model=Merchant)
async def read_merchant(merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Merchant:
    db_merchant = await session.get(DBMerchant, merchant_id)
    if db_merchant:
        return Merchant.from_orm(db_merchant)
    raise HTTPException(status_code=404, detail="Merchant not found")

@router.put("/{merchant_id}", response_model=Merchant)
async def update_merchant(merchant_id: int, merchant: UpdateMerchant, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Merchant:
    db_merchant = await session.get(DBMerchant, merchant_id)
    if db_merchant:
        for key, value in merchant.dict().items():
            setattr(db_merchant, key, value)
        session.add(db_merchant)
        await session.commit()
        await session.refresh(db_merchant)
        return Merchant.from_orm(db_merchant)
    raise HTTPException(status_code=404, detail="Merchant not found")

@router.delete("/{merchant_id}")
async def delete_merchant(merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> dict:
    db_merchant = session.get(Merchant, merchant_id)
    if db_merchant:
        await session.delete(db_merchant)
        await session.commit()
        return {"message": "Merchant and item deleted successfully"}
    raise HTTPException(status_code=404, detail="Merchant not found")