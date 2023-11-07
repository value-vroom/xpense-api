"""This router is used to manage transactions"""
from fastapi import APIRouter, Depends

from prisma import get_client
from prisma.models import Transaction
from typing import Annotated

from prisma.models import User

from app.utility.security import get_current_user
from app.routers.groups import get_group_members, get_group_balance

router = APIRouter(tags=["Transactions"])


@router.get("/groups/{group_id}/transactions")
def get_transactions(
    group_id: int, current_user: Annotated[User, Depends(get_current_user)]
) -> list[Transaction]:
    """Get all transactions"""
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

    return db.transaction.find_many(where={"group_id": group_id})


@router.post("/groups/{group_id}/transactions")
def create_transaction(
    group_id: int,
    amount_in_cents: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Transaction:
    """Create a new transaction"""
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

    # Check if the the group balance permits the transaction
    group_members = get_group_members(group_id, current_user)
    current_group_member = next(
        (member for member in group_members if member["username"] == current_user.username),
        None,
    )

    if not current_group_member:
        raise Exception("You are not a member of this group")

    if amount_in_cents == 0:
        raise Exception("You cannot make a transaction of 0")

    if amount_in_cents < 0:
        # Withdrawing money
        if current_group_member["balance_amount_cents"] + amount_in_cents < 0:
            raise Exception("You cannot withdraw more than your balance")

        if get_group_balance(group_id, current_user).balance_amount_cents + amount_in_cents < 0:
            raise Exception("You cannot withdraw more than the group balance")

    else:  # noqa: PLR5501
        # Depositing money
        if current_group_member["balance_amount_cents"] + amount_in_cents > 0:
            raise Exception("You cannot deposit more than what you owe")

    # We need to get the last id, and increment it by one
    last_transaction = db.transaction.find_first(
        where={"group_id": group_id},
        order={"id": "desc"},
    )

    return db.transaction.create(
        data={
            "id": last_transaction.id + 1 if last_transaction else 1,
            "group_id": group_id,
            "amount_in_cents": amount_in_cents,
            "username": current_user.username,
        },
    )
