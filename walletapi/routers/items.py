from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import Session, select
from models.item import ItemBase
from models.dbmodels import Item, Merchant

from models import get_session

router = APIRouter(prefix="/items", tags=["Item"])

@router.get("",response_model=list[Item])
async def read_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()

@router.post("/{merchant.id}", response_model=Item)
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

@router.get("/{wallet_id}", response_model=Item)
async def read_item(item_id: int, session: Session = Depends(get_session)):
    db_item = session.get(Item, item_id)
    if db_item:
        return db_item
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{wallet_id}", response_model=Item)
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

@router.delete("/{wallet_id}")
async def delete_item(item_id: int, session: Session = Depends(get_session)):
    db_item = session.get(Item, item_id)
    if db_item:
        session.delete(db_item)
        session.commit()
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")