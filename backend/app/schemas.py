from pydantic import BaseModel, EmailStr, constr, confloat
from datetime import datetime
from typing import Optional


# Common base class for expense schemas
class ExpenseSchemaBase(BaseModel):
    category: constr(min_length=1)
    amount: confloat(ge=0)
    description: Optional[str] = None
    date: datetime


class ExpenseBase(ExpenseSchemaBase):
    payment_method: constr(min_length=1)


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


class ExpenseSplitBase(BaseModel):
    amount: float
    paid: bool = False


class ExpenseSplitCreate(ExpenseSplitBase):
    user_id: int


class ExpenseSplit(ExpenseSplitBase):
    id: int
    expense_id: int
    user_id: int

    class Config:
        from_attributes = True  # Updated from orm_mode


class GroupExpenseBase(ExpenseSchemaBase):
    split_type: str = "equal"
    custom_splits: Optional[dict[int, float]] = None


class GroupExpenseCreate(GroupExpenseBase):
    pass


class GroupExpense(GroupExpenseBase):
    id: int
    date: datetime
    paid_by: int
    splits: list[ExpenseSplit]
    user_split: Optional[float] = None  # Amount this user owes/is owed
    is_paid_by_user: Optional[bool] = None  # Whether current user paid this expense

    class Config:
        from_attributes = True


class GroupBase(BaseModel):
    name: constr(min_length=1)


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode


class GroupMemberBase(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        from_attributes = True

class GroupMember(GroupMemberBase):
    joined_at: datetime
