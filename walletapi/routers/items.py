from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models

from ..models.item import Item, CreateItem, UpdateItem, ItemList
from ..models.dbmodels import DBItem, DBMerchant

router = APIRouter(prefix="/items", tags=["Item"])

@router.get("",response_model=list[Item])
async def read_items(session: Annotated[AsyncSession, Depends(models.get_session)], page: int = 1, page_size: int = 10,) -> ItemList:
    result = await session.exec(
        select(DBItem).offset((page - 1) * page_size).limit(page_size)
    )
    db_items = result.all()

    return ItemList(
        items=db_items, page=page, page_size=page_size, size_per_page=len(db_items)
    )

@router.post("/{merchant.id}", response_model=Item)
async def create_item(item: CreateItem, merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)],) -> Item:
    db_item = DBItem(**item.dict())
    db_item.merchant_id = merchant_id
    if merchant_id:
        merchant = session.get(DBMerchant, DBItem.merchant_id)
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        db_item.merchant = merchant
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return Item.from_orm(db_item)

@router.get("/{wallet_id}", response_model=Item)
async def read_item(item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)],) -> Item:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{wallet_id}", response_model=Item)
async def update_item(item_id: int, item: UpdateItem, session: Annotated[AsyncSession, Depends(models.get_session)],) -> Item:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        for key, value in item.dict().items():
            setattr(db_item, key, value)
        session.add(db_item)
        await session.commit()
        await session.refresh(db_item)
        return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{wallet_id}")
async def delete_item(item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)],) -> dict:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        await session.delete(db_item)
        await session.commit()
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")