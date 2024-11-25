from datetime import datetime
# from typing import Optional
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


def validate_expense_data(amount: float, category: str, date: datetime):
    if amount < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Amount must be positive"
        )
    if not category.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category cannot be empty"
        )
    if not date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Date is required"
        )

    return date


def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    date = validate_expense_data(expense.amount, expense.category, expense.date)

    if not expense.payment_method.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payment method cannot be empty"
        )

    db_expense = models.Expense(
        date=date,
        category=expense.category,
        amount=expense.amount,
        description=expense.description,
        payment_method=expense.payment_method,
        user_id=user_id
    )
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


def create_group(db: Session, name: str, user_id: int):
    group = models.Group(name=name, created_by=user_id)
    member = models.GroupMember(user_id=user_id)
    group.members.append(member)

    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def join_group(db: Session, group_id: int, user_id: int):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if any(member.user_id == user_id for member in group.members):
        raise HTTPException(status_code=400, detail="Already a member")

    member = models.GroupMember(user_id=user_id, group_id=group.id)
    db.add(member)
    db.commit()
    return member


def create_group_expense(db: Session, group_id: int, expense: schemas.GroupExpenseCreate, paid_by: int):
    date = validate_expense_data(expense.amount, expense.category, expense.date)

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    db_expense = models.GroupExpense(
        group_id=group.id,
        paid_by=paid_by,
        date=date,
        amount=expense.amount,
        category=expense.category,
        description=expense.description
    )

    member_count = len(group.members)
    if expense.split_type == "equal":
        split_amount = expense.amount / member_count
        for member in group.members:
            split = models.ExpenseSplit(
                user_id=member.user_id,
                amount=split_amount
            )
            db_expense.splits.append(split)
    else:
        if not expense.custom_splits:
            raise HTTPException(
                status_code=400,
                detail="Custom splits required when split_type is not 'equal'"
            )

        total_percentage = sum(expense.custom_splits.values())
        if not abs(total_percentage - 100) < 0.01:
            raise HTTPException(
                status_code=400,
                detail="Split percentages must sum to 100"
            )

        for user_id, percentage in expense.custom_splits.items():
            split = models.ExpenseSplit(
                user_id=user_id,
                amount=(percentage / 100) * expense.amount
            )
            db_expense.splits.append(split)

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_group_expenses(
    db: Session,
    group_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    is_member = db.query(models.GroupMember).filter(
        models.GroupMember.group_id == group.id,
        models.GroupMember.user_id == user_id
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this group")

    expenses = db.query(models.GroupExpense).filter(
        models.GroupExpense.group_id == group.id
    ).offset(skip).limit(limit).all()

    for expense in expenses:
        expense.user_split = next(
            (split.amount for split in expense.splits if split.user_id == user_id),
            0
        )
        expense.is_paid_by_user = expense.paid_by == user_id

    return expenses


def delete_group_expense(
    db: Session,
    group_id: int,
    expense_id: int,
    user_id: int
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    expense = db.query(models.GroupExpense).filter(
        models.GroupExpense.id == expense_id,
        models.GroupExpense.group_id == group.id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.paid_by != user_id and group.created_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only expense creator or group admin can delete expenses"
        )

    db.query(models.ExpenseSplit).filter(
        models.ExpenseSplit.expense_id == expense_id
    ).delete()

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted successfully"}


def get_user_groups(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    member_groups = db.query(models.Group).join(models.GroupMember).filter(
        models.GroupMember.user_id == user_id
    ).offset(skip).limit(limit).all()
    return member_groups
