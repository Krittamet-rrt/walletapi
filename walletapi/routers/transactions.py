from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import select
from models.transaction import Transaction, UpdateTransaction, TransactionList
from models.dbmodels import DBTransaction

from typing import Annotated

from sqlmodel.ext.asyncio.session import AsyncSession

import models

router = APIRouter(prefix="/transactions", tags=["Transaction"])

@router.get("",response_model=list[Transaction])
async def read_transactions(session: Annotated[AsyncSession, Depends(models.get_session)], page: int = 1, page_size: int = 10,) -> TransactionList:
    result = await session.exec(
        select(DBTransaction).offset((page - 1) * page_size).limit(page_size)
    )
    db_transactions = result.all()
    return TransactionList(
        transactions=db_transactions,
        page=page,
        page_size=page_size,
        size_per_page=len(db_transactions),
    )

@router.get("/{transaction_id}", response_model=Transaction)
async def read_transaction(transaction_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Transaction:
    db_transaction = await session.get(DBTransaction, transaction_id)
    if db_transaction:
        return Transaction.from_orm(db_transaction)
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
        return Transaction.from_orm(db_transaction)
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]) -> Transaction:
    db_transaction = session.get(DBTransaction, transaction_id)
    if db_transaction:
        session.delete(db_transaction)
        session.commit()
        return {"message": "Transaction deleted successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found")