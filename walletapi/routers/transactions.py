from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import select, func
from ..models.transaction import Transaction, UpdateTransaction, TransactionList
from ..models.dbmodels import DBTransaction

from typing import Annotated

from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models
import math

router = APIRouter(prefix="/transactions", tags=["Transaction"])

SIZE_PER_PAGE = 50

@router.get("",response_model=TransactionList)
async def read_transactions(session: Annotated[AsyncSession, Depends(models.get_session)], page: int = 1) -> TransactionList:
    result = await session.exec(
        select(DBTransaction).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    db_transaction = result.all()

    page_count = int(
        math.ceil((await session.exec(select(func.count(DBTransaction.id)))).first()/SIZE_PER_PAGE)
    )

    print("page_count", page_count)
    print("transaction", db_transaction)

    return TransactionList(transaction=db_transaction, page=page, page_count=page_count, size_per_page=SIZE_PER_PAGE)

@router.get("/{transaction_id}", response_model=Transaction)
async def read_transaction(transaction_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Transaction:
    db_transaction = await session.get(DBTransaction, transaction_id)
    if db_transaction:
        return Transaction.model_validate(db_transaction)
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: int, transaction: UpdateTransaction, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Transaction:
    db_transaction = await session.get(DBTransaction, transaction_id)
    if db_transaction:
        for key, value in transaction.dict().items():
            setattr(db_transaction, key, value)
        session.add(db_transaction)
        await session.commit()
        await session.refresh(db_transaction)
        return Transaction.model_validate(db_transaction)
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Transaction:
    db_transaction = session.get(DBTransaction, transaction_id)
    if db_transaction:
        session.delete(db_transaction)
        session.commit()
        return {"message": "Transaction deleted successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found")