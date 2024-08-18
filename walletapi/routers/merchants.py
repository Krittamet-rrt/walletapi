from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import select
from models.merchant import Merchant, CreateMerchant, UpdateMerchant, MerchantList
from models.dbmodels import DBMerchant

from typing import Annotated

from sqlmodel import select, func

from sqlmodel.ext.asyncio.session import AsyncSession

from models.user import User

import models
import deps
import math

router = APIRouter(prefix="/merchants", tags=["Merchant"])

@router.post("", response_model=Merchant)
async def create_merchant(merchant: CreateMerchant, current_user: Annotated[User, Depends(deps.get_current_user)], session: Annotated[AsyncSession, Depends(models.get_session)]) -> Merchant:
    db_merchant = DBMerchant(**merchant.dict())
    db_merchant.user = current_user
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)
    return Merchant.from_orm(db_merchant)

SIZE_PER_PAGE = 50

@router.get("",response_model=MerchantList)
async def read_merchants(session: Annotated[AsyncSession, Depends(models.get_session)], page: int = 1) -> MerchantList:
    result = await session.exec(
        select(DBMerchant).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    db_merchant = result.all()

    page_count = int(
        math.ceil((await session.exec(select(func.count(DBMerchant.id)))).first()/SIZE_PER_PAGE)
    )

    print("page_count", page_count)
    print("merchant", db_merchant)

    return MerchantList(merchant=db_merchant, page=page, page_count=page_count, size_per_page=SIZE_PER_PAGE)


@router.get("/{merchant_id}", response_model=Merchant)
async def read_merchant(merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Merchant:
    db_merchant = await session.get(DBMerchant, merchant_id)
    if db_merchant:
        return Merchant.from_orm(db_merchant)
    raise HTTPException(status_code=404, detail="Merchant not found")

@router.put("/{merchant_id}", response_model=Merchant)
async def update_merchant(merchant_id: int, current_user: Annotated[User, Depends(deps.get_current_user)], merchant: UpdateMerchant, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Merchant:
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
async def delete_merchant(merchant_id: int, current_user: Annotated[User, Depends(deps.get_current_user)], session: Annotated[AsyncSession, Depends(models.get_session)]) -> dict:
    db_merchant = session.get(Merchant, merchant_id)
    if db_merchant:
        await session.delete(db_merchant)
        await session.commit()
        return {"message": "Merchant and item deleted successfully"}
    raise HTTPException(status_code=404, detail="Merchant not found")