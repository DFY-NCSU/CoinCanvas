from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ExpenseBase(BaseModel):
    category: str
    amount: float
    description: Optional[str] = None
    payment_method: str

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    date: datetime
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    expenses: list[Expense] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None