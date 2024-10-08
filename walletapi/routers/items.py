from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models
from .. import deps
import math

from ..models.item import Item, CreateItem, UpdateItem, ItemList
from ..models.user import User
from ..models.dbmodels import DBItem, DBMerchant

router = APIRouter(prefix="/items", tags=["Item"])

SIZE_PER_PAGE = 50

@router.get("", response_model=ItemList)
async def read_items(session: Annotated[AsyncSession, Depends(models.get_session)], page: int = 1) -> ItemList:
    result = await session.exec(
        select(DBItem).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    db_items = result.all()

    page_count = int(
        math.ceil((await session.exec(select(func.count(DBItem.id)))).first()/SIZE_PER_PAGE)
    )

    print("page_count", page_count)
    print("items", db_items)

    return ItemList.model_validate(items=db_items, page=page, page_count=page_count, size_per_page=SIZE_PER_PAGE)
    

@router.post("/{merchant.id}", response_model=Item)
async def create_item(item: CreateItem, merchant_id: int, current_user: Annotated[User, Depends(deps.get_current_user)], session: Annotated[AsyncSession, Depends(models.get_session)],) -> Item:
    db_item = DBItem.model_validate(item)
    db_item.merchant_id = merchant_id
    if merchant_id:
        merchant = await session.get(DBMerchant, merchant_id)
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        db_item.merchant = merchant
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return Item.model_validate(db_item)

@router.get("/{wallet_id}", response_model=Item)
async def read_item(item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)],) -> Item:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        return Item.model_validate(db_item)
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{wallet_id}", response_model=Item)
async def update_item(item_id: int, item: UpdateItem, current_user: Annotated[User, Depends(deps.get_current_user)], session: Annotated[AsyncSession, Depends(models.get_session)],) -> Item:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        for key, value in item.dict().items():
            setattr(db_item, key, value)
        session.add(db_item)
        await session.commit()
        await session.refresh(db_item)
        return Item.model_validate(db_item)
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{wallet_id}")
async def delete_item(item_id: int, current_user: Annotated[User, Depends(deps.get_current_user)], session: Annotated[AsyncSession, Depends(models.get_session)],) -> dict:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        await session.delete(db_item)
        await session.commit()
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

