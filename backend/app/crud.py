from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    # Additional validation for empty strings
    if not user.password.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password cannot be empty"
        )
    if not user.full_name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full name cannot be empty"
        )

    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # Validate skip and limit parameters
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Skip value cannot be negative"
        )
    if limit < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit value cannot be negative"
        )

    return db.query(models.Expense)\
             .filter(models.Expense.user_id == user_id)\
             .offset(skip)\
             .limit(limit)\
             .all()


def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    # Additional validation for amount and empty strings
    if expense.amount < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Amount must be positive"
        )
    if not expense.category.strip() or not expense.payment_method.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category and payment method cannot be empty"
        )

    db_expense = models.Expense(**expense.dict(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int, user_id: int):
    expense = db.query(models.Expense)\
                .filter(models.Expense.id == expense_id)\
                .filter(models.Expense.user_id == user_id)\
                .first()
    if expense:
        db.delete(expense)
        db.commit()
    return expense
