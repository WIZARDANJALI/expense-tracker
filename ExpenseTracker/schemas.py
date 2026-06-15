from pydantic import BaseModel, EmailStr
from typing import Optional


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str
    
class BudgetCreate(BaseModel):
    month: str
    budget_amount: float


class BudgetUpdate(BaseModel):
    month: Optional[str] = None
    budget_amount: Optional[float] = None