from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from .. import crud, schemas, models
from ..database import get_db
from .users import get_current_user

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)

@router.get("/", response_model=List[schemas.Expense])
async def read_expenses(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all expenses with optional filtering parameters
    """
    query = db.query(models.Expense).filter(models.Expense.user_id == current_user.id)
    
    if category:
        query = query.filter(models.Expense.category == category)
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    if min_amount:
        query = query.filter(models.Expense.amount >= min_amount)
    if max_amount:
        query = query.filter(models.Expense.amount <= max_amount)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Expense)
async def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new expense
    """
    return crud.create_expense(db=db, expense=expense, user_id=current_user.id)

@router.get("/{expense_id}", response_model=schemas.Expense)
async def read_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a specific expense by ID
    """
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == current_user.id
    ).first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.put("/{expense_id}", response_model=schemas.Expense)
async def update_expense(
    expense_id: int,
    expense_update: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an expense
    """
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == current_user.id
    ).first()
    
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    for key, value in expense_update.dict().items():
        setattr(db_expense, key, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete an expense
    """
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == current_user.id
    ).first()
    
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(db_expense)
    db.commit()
    return {"message": "Expense deleted successfully"}

@router.get("/statistics/summary")
async def get_expense_statistics(
    timeframe: str = Query("month", enum=["day", "week", "month", "year"]),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get expense statistics summary
    """
    now = datetime.utcnow()
    
    if timeframe == "day":
        start_date = now - timedelta(days=1)
    elif timeframe == "week":
        start_date = now - timedelta(weeks=1)
    elif timeframe == "month":
        start_date = now - timedelta(days=30)
    else:  # year
        start_date = now - timedelta(days=365)
    
    expenses = db.query(models.Expense).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= start_date
    ).all()
    
    total_amount = sum(expense.amount for expense in expenses)
    category_breakdown = {}
    for expense in expenses:
        category_breakdown[expense.category] = category_breakdown.get(expense.category, 0) + expense.amount
    
    return {
        "timeframe": timeframe,
        "total_expenses": len(expenses),
        "total_amount": total_amount,
        "average_amount": total_amount / len(expenses) if expenses else 0,
        "category_breakdown": category_breakdown
    }