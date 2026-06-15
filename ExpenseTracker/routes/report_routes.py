from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from models import User, Expense, Budget
from auth import get_current_user_email

router = APIRouter()

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard")
def dashboard(
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

    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"User not found: {email}"
        )

    total_expense = db.query(
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user.id
    ).scalar() or 0

    total_budget = db.query(
        func.sum(Budget.budget_amount)
    ).filter(
        Budget.user_id == user.id
    ).scalar() or 0

    return {
        "total_budget": total_budget,
        "total_expense": total_expense,
        "remaining": total_budget - total_expense
    }


@router.get("/expenses/category-summary")
def category_summary(
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

    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"User not found: {email}"
        )

    result = db.query(
        Expense.category,
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user.id
    ).group_by(
        Expense.category
    ).all()

    return [
        {
            "category": row[0],
            "total": row[1]
        }
        for row in result
    ]


@router.get("/budget-report")
def budget_report(
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

    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"User not found: {email}"
        )

    total_expense = db.query(
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user.id
    ).scalar() or 0

    total_budget = db.query(
        func.sum(Budget.budget_amount)
    ).filter(
        Budget.user_id == user.id
    ).scalar() or 0

    remaining = total_budget - total_expense

    utilization = 0

    if total_budget > 0:
        utilization = (total_expense / total_budget) * 100

    return {
        "budget": total_budget,
        "spent": total_expense,
        "remaining": remaining,
        "utilization_percentage": round(utilization, 2)
    }