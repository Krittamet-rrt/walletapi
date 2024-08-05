from fastapi import APIRouter, HTTPException, Depends

from sqlmodel import Session, select
from models.transaction import TransactionBase
from models.dbmodels import Transaction

from models import get_session

router = APIRouter(prefix="/transactions", tags=["Transaction"])

@router.get("",response_model=list[Transaction])
async def read_transactions(session: Session = Depends(get_session)):
    return session.exec(select(Transaction)).all()

@router.get("/{transaction_id}", response_model=Transaction)
async def read_transaction(transaction_id: int, session: Session = Depends(get_session)):
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction:
        return db_transaction
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: int, transaction: TransactionBase, session: Session = Depends(get_session)):
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction:
        for key, value in transaction.dict().items():
            setattr(db_transaction, key, value)
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)
        return db_transaction
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction:
        session.delete(db_transaction)
        session.commit()
        return {"message": "Transaction deleted successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found")