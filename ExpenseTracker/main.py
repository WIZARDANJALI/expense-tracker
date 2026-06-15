from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from routes.report_routes import router as report_router

from database import Base, engine, SessionLocal
from schemas import (
    UserCreate,
    UserLogin,
    ExpenseCreate,
    ExpenseUpdate,
    BudgetCreate,
    BudgetUpdate
)
from models import User, Expense, Budget
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    get_current_user_email
)

app = FastAPI(title="Expense Tracker API")

app.include_router(report_router)

Base.metadata.create_all(bind=engine)

security = HTTPBearer()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "API is running"}


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        return {"message": "User not found"}

    if not verify_password(
        user.password,
        db_user.password
    ):
        return {"message": "Invalid password"}

    token = create_access_token(
        {"sub": db_user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/profile")
def profile(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return {
        "message": "Protected Route Accessed",
        "user": payload["sub"]
    }

@app.post("/expenses")
def create_expense(
    expense: ExpenseCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    email = get_current_user_email(token)

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    new_expense = Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        user_id=user.id
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return {
        "message": "Expense added successfully",
        "expense_id": new_expense.id
    }
    
@app.get("/expenses")
def get_expenses(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    email = get_current_user_email(token)

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    expenses = db.query(Expense).filter(
        Expense.user_id == user.id
    ).all()

    return expenses

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, updated_data: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    # update fields
    if updated_data.title is not None:
        expense.title = updated_data.title

    if updated_data.amount is not None:
        expense.amount = updated_data.amount

    if updated_data.category is not None:
        expense.category = updated_data.category

    db.commit()
    db.refresh(expense)

    return {
        "message": "Expense updated successfully",
        "updated_expense": expense
    }
    
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return {
        "message": "Expense deleted successfully"
    }
    
@app.post("/budget")
def create_budget(
    budget: BudgetCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    email = get_current_user_email(token)

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    new_budget = Budget(
        month=budget.month,
        budget_amount=budget.budget_amount,
        user_id=user.id
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return {
        "message": "Budget created successfully",
        "budget_id": new_budget.id
    }
    
@app.post("/budgets")
def create_multiple_budgets(
    budgets: List[BudgetCreate],
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    email = get_current_user_email(token)

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    created_budgets = []

    for budget in budgets:

        new_budget = Budget(
            month=budget.month,
            budget_amount=budget.budget_amount,
            user_id=user.id
        )

        db.add(new_budget)
        created_budgets.append(new_budget)

    db.commit()

    return {
        "message": f"{len(created_budgets)} budgets added successfully"
    }

@app.get("/budget")
def get_budget(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    email = get_current_user_email(token)

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    budgets = db.query(Budget).filter(
        Budget.user_id == user.id
    ).all()

    return budgets

@app.put("/budget/{budget_id}")
def update_budget(
    budget_id: int,
    updated_budget: BudgetUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    email = get_current_user_email(token)

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user.id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    if updated_budget.month is not None:
        budget.month = updated_budget.month

    if updated_budget.budget_amount is not None:
        budget.budget_amount = updated_budget.budget_amount

    db.commit()
    db.refresh(budget)

    return {
        "message": "Budget updated successfully"
    }