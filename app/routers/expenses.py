"""This router is used to manage expenses"""
from fastapi import APIRouter, Depends

from prisma import get_client
from prisma.models import Expense, ExpenseMember
from typing import Annotated
from pydantic import BaseModel

from prisma.models import User

from app.utility.security import get_current_user

router = APIRouter(tags=["Expenses"])


@router.get("/groups/{group_id}/expenses")
def get_expenses(group_id: int, current_user: Annotated[User, Depends(get_current_user)]) -> list[Expense]:
    """Get all expenses"""
    db = get_client()

    # Check if the current user is a member of the group
    group_member = db.groupmember.find_first(
        where={
            "username": current_user.username,
            "group_id": group_id,
        },
    )

    if not group_member:
        raise Exception("You are not a member of this group")

    return db.expense.find_many(where={"group_id": group_id})


class CreateMemberModel(BaseModel):
    username: str
    amount_in_cents: int


class CreateExpenseModel(BaseModel):
    name: str
    description: str
    amount_in_cents: int
    payer_username: str
    members: list[CreateMemberModel]


@router.post("/groups/{group_id}/expenses")
def create_expense(  # noqa: PLR0913
    group_id: int,
    expense: CreateExpenseModel,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Expense:
    """Create a new expense"""
    db = get_client()

    # Check if the current user is a member of the group
    group_member = db.groupmember.find_first(
        where={
            "username": current_user.username,
            "group_id": group_id,
        },
    )

    if not group_member:
        raise Exception("You are not a member of this group")

    # Check if the expense amount is equal to the sum of the members
    if sum([member.amount_in_cents for member in expense.members]) != expense.amount_in_cents:
        raise Exception("The expense amount is not equal to the sum of the members")

    # Check that all members are part of the group
    group_members = db.groupmember.find_many(
        where={
            "username": {"in": [member.username for member in expense.members]},
            "group_id": group_id,
        },
    )

    if len(group_members) != len(expense.members):
        raise Exception("Not all members are part of the group")

    # We need to get the last id, and increment it by one
    last_expense = db.expense.find_first(
        where={"group_id": group_id},
        order={"id": "desc"},
    )

    expense_response = db.expense.create(
        data={
            "id": last_expense.id + 1 if last_expense else 1,
            "name": expense.name,
            "description": expense.description,
            "amount_in_cents": expense.amount_in_cents,
            "group_id": group_id,
            "payer_username": expense.payer_username,
        },
    )

    for member in expense.members:
        db.expensemember.create(
            data={
                "username": member.username,
                "expense_id": expense_response.id,
                "group_id": group_id,
                "amount_in_cents": member.amount_in_cents,
            },
        )

    return expense_response


@router.get("/groups/{group_id}/expenses/{expense_id}")
def get_expense(
    group_id: int,
    expense_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Expense:
    """Get a specific expense"""
    db = get_client()

    # Check if the current user is a member of the group
    group_member = db.groupmember.find_first(
        where={
            "username": current_user.username,
            "group_id": group_id,
        },
    )

    if not group_member:
        raise Exception("You are not a member of this group")

    expense = db.expense.find_first(
        where={
            "group_id": group_id,
            "id": expense_id,
        },
    )

    if not expense:
        raise Exception("Expense not found")

    return expense


@router.get("/groups/{group_id}/expenses/{expense_id}/members")
def get_expense_members(
    group_id: int,
    expense_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[ExpenseMember]:
    """Get all expense members"""
    db = get_client()

    # Check if the current user is a member of the group
    group_member = db.groupmember.find_first(
        where={
            "username": current_user.username,
            "group_id": group_id,
        },
    )

    if not group_member:
        raise Exception("You are not a member of this group")

    expense = db.expense.find_first(
        where={
            "group_id": group_id,
            "id": expense_id,
        },
    )

    if not expense:
        raise Exception("Expense not found")

    return db.expensemember.find_many(
        where={
            "group_id": group_id,
            "expense_id": expense_id,
        },
    )
