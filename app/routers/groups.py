"""This router is used to get the groups"""
from typing import Annotated

from fastapi import APIRouter, Depends
from prisma.models import User, Group, GroupMember as GroupMemberModel
from pydantic import BaseModel
from app.utility.security import get_current_user
from prisma import get_client

router = APIRouter(tags=["Groups"])


class GroupMember(GroupMemberModel):
    """GroupMember model"""

    balance_amount_cents: int


@router.get("/groups", operation_id="get_groups")
def get_groups(current_user: Annotated[User, Depends(get_current_user)]) -> list[Group]:
    """Get all groups where the user is a member of"""
    db = get_client()

    group_members = db.groupmember.find_many(
        where={"username": current_user.username},
        include={"group": True},
    )

    return [group_member.group for group_member in group_members]


@router.post("/groups", operation_id="create_group")
def create_group(
    name: str,
    description: str,
    currency_code: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Group:
    """Create a new group"""
    db = get_client()

    group = db.group.create(
        data={
            "name": name,
            "description": description,
            "currency_code": currency_code,
        },
    )

    db.groupmember.create(
        data={
            "username": current_user.username,
            "group_id": group.id,
            "is_owner": True,
        },
    )

    return group


@router.get("/groups/{group_id}", operation_id="get_group")
def get_group(group_id: int, current_user: Annotated[User, Depends(get_current_user)]) -> Group:
    """Get a specific group"""
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

    return db.group.find_first(where={"id": group_id})


@router.get("/groups/{group_id}/members", operation_id="get_group_members")
def get_group_members(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[GroupMember]:
    """Get all members of a group"""
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

    group_members = [
        group_member.dict() for group_member in db.groupmember.find_many(where={"group_id": group_id})
    ]

    # Calculate the balance of each member
    for member in group_members:
        member["balance_amount_cents"] = 0

        for expense in db.expense.find_many(where={"group_id": group_id}):
            if expense.payer_username == member["username"]:
                member["balance_amount_cents"] += expense.amount_in_cents

            expense_member = db.expensemember.find_first(
                where={
                    "expense_id": expense.id,
                    "group_id": group_id,
                    "username": member["username"],
                },
            )

            if expense_member:
                member["balance_amount_cents"] -= expense_member.amount_in_cents

        for transaction in db.transaction.find_many(
            where={"group_id": group_id, "username": member["username"]}
        ):
            member["balance_amount_cents"] += transaction.amount_in_cents

    return group_members


@router.post("/groups/{group_id}/members", operation_id="add_group_member")
def add_group_member(
    group_id: int,
    username: str,
    is_owner: bool,
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[GroupMemberModel]:
    """Add a user to a group"""
    db = get_client()

    # Check if the current user is the owner of the group
    group_member = db.groupmember.find_first(
        where={
            "username": current_user.username,
            "group_id": group_id,
            "is_owner": True,
        },
    )

    if not group_member:
        raise Exception("You are not the owner of this group")

    db.groupmember.create(
        data={
            "username": username,
            "group_id": group_id,
            "is_owner": is_owner,
        },
    )

    return db.groupmember.find_many(where={"group_id": group_id})


@router.delete("/groups/{group_id}/members/{username}", operation_id="remove_group_member")
def remove_group_member(
    group_id: int,
    username: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[GroupMember]:
    """Remove a user from a group"""
    db = get_client()

    # Check if the current user is the owner of the group
    group_member = db.groupmember.find_first(
        where={
            "username": current_user.username,
            "group_id": group_id,
            "is_owner": True,
        },
    )

    if not group_member:
        raise Exception("You are not the owner of this group")

    db.groupmember.delete(
        where={
            "username": username,
            "group_id": group_id,
        },
    )

    return db.groupmember.find_many(where={"group_id": group_id})


class GroupBalance(BaseModel):
    """GroupBalance model"""

    balance_amount_cents: int


@router.get("/groups/{group_id}/balance", operation_id="get_group_balance")
def get_group_balance(
    group_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> GroupBalance:
    """Get the balance of a group"""
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

    group_balance = GroupBalance(balance_amount_cents=0)

    for transaction in db.transaction.find_many(where={"group_id": group_id}):
        group_balance.balance_amount_cents += transaction.amount_in_cents

    return group_balance
