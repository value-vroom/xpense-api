"""This router is used to get the groups"""
from typing import Annotated

from fastapi import APIRouter, Depends
from prisma.models import User, Group, GroupMember

from app.utility.security import get_current_user
from prisma import get_client

router = APIRouter(tags=["Groups"])


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
    name: str, description: str, current_user: Annotated[User, Depends(get_current_user)]
) -> Group:
    """Create a new group"""
    db = get_client()

    group = db.group.create(
        data={
            "name": name,
            "description": description,
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


@router.post("/groups/{group_id}/members", operation_id="add_group_member")
def add_group_member(
    group_id: int,
    username: str,
    is_owner: bool,
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[GroupMember]:
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
