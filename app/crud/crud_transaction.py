# app/crud/crud_transaction.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.transaction import Transaction, PaymentRecord
from app.schemas.transaction import TransactionCreate, TransactionUpdate, PaymentRecordCreate, PaymentRecordUpdate


def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    """Create a new transaction."""
    db_transaction = Transaction(
        produce_listing_id=transaction.produce_listing_id,
        seller_id=transaction.seller_id,
        buyer_id=transaction.buyer_id,
        agreed_price_per_kg=transaction.agreed_price_per_kg,
        quantity_kg=transaction.quantity_kg,
        total_amount=transaction.total_amount,
        status=transaction.status
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def get_transaction(db: Session, transaction_id: str) -> Optional[Transaction]:
    """Get a transaction by ID."""
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_transactions(db: Session, skip: int = 0, limit: int = 100, buyer_id: Optional[str] = None, seller_id: Optional[str] = None) -> List[Transaction]:
    """Get a list of transactions."""
    query = db.query(Transaction)
    if buyer_id:
        query = query.filter(Transaction.buyer_id == buyer_id)
    if seller_id:
        query = query.filter(Transaction.seller_id == seller_id)
    return query.offset(skip).limit(limit).all()


def update_transaction(db: Session, transaction_id: str, transaction_update: TransactionUpdate) -> Optional[Transaction]:
    """Update a transaction."""
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        update_data = transaction_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_transaction, field, value)
        db.commit()
        db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: str) -> bool:
    """Delete a transaction."""
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return True
    return False


def update_transaction_status(db: Session, transaction_id: str, status) -> Optional[Transaction]:
    """Update the status of a transaction."""
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        db_transaction.status = status
        db.commit()
        db.refresh(db_transaction)
    return db_transaction


def create_payment_record(db: Session, payment_record: PaymentRecordCreate, transaction_id: str) -> PaymentRecord:
    """Create a new payment record."""
    db_payment_record = PaymentRecord(
        transaction_id=transaction_id,
        payment_method=payment_record.payment_method,
        amount=payment_record.amount,
        currency=payment_record.currency,
        reference=payment_record.reference,
        status=payment_record.status,
        paystack_data=payment_record.paystack_data
    )
    db.add(db_payment_record)
    db.commit()
    db.refresh(db_payment_record)
    return db_payment_record


def get_payment_record(db: Session, payment_record_id: str) -> Optional[PaymentRecord]:
    """Get a payment record by ID."""
    return db.query(PaymentRecord).filter(PaymentRecord.id == payment_record_id).first()


def update_payment_record(db: Session, payment_record_id: str, payment_record_update: PaymentRecordUpdate) -> Optional[PaymentRecord]:
    """Update a payment record."""
    db_payment_record = get_payment_record(db, payment_record_id)
    if db_payment_record:
        update_data = payment_record_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_payment_record, field, value)
        db.commit()
        db.refresh(db_payment_record)
    return db_payment_record