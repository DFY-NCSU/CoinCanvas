from pydantic import BaseModel, EmailStr, constr, confloat
from datetime import datetime
from typing import Optional


class ExpenseBase(BaseModel):
    category: constr(min_length=1)  # Non-empty string
    amount: confloat(ge=0)  # Must be greater than or equal to 0
    description: Optional[str] = None
    payment_method: constr(min_length=1)  # Non-empty string


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
    full_name: constr(min_length=1)  # Non-empty string


class UserCreate(UserBase):
    password: constr(min_length=1)  # Non-empty string


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
