"""This is a helper library, which seeds the database with some data"""
import json
import pathlib
import subprocess
import app
from app.utility import security
from prisma import Prisma, get_client, register, Base64


def clamp(n: int, minn: int, maxn: int) -> int:
    """Clamp a number between a min and max value"""
    return max(min(maxn, n), minn)


def delete_db() -> None:
    """Delete the database"""
    database_dir = (pathlib.Path(app.__file__).parent.parent / "prisma" / "database.db").resolve()
    subprocess.run(["rm", "-f", database_dir], check=True)  # noqa: S603, S607
    subprocess.run(["prisma", "db", "push"], check=True)  # noqa: S603, S607


def register_prisma() -> None:
    """Register the Prisma client"""
    db = Prisma()
    db.connect()
    register(db)


def seed_db() -> None:  # noqa: C901
    """Seeds the database with some data"""
    db = get_client()

    # Seeds dir
    seeds_dir = pathlib.Path(app.__file__).parent.parent / "seeds"

    # Setup images
    # iterate over all images in the images directory
    images_dir = seeds_dir / "images"
    for image in images_dir.iterdir():
        db.image.create(data={"name": image.name, "data": Base64.encode(image.read_bytes())})

    # Setup users
    users = json.loads((seeds_dir / "users.json").read_text())
    users_db = []
    for user in users:
        user["hashed_password"] = security.get_password_hash(user["password"])
        del user["password"]
        users_db.append(db.user.create(data=user))

    # Setup currencies
    currencies = json.loads((seeds_dir / "currencies.json").read_text())
    for currency in currencies:
        db.currency.create(data=currency)

    # Setup groups
    groups = json.loads((seeds_dir / "groups.json").read_text())
    for group in groups:
        db.group.create(data=group)

    # Setup group members
    group_members = json.loads((seeds_dir / "group_members.json").read_text())
    for group_member in group_members:
        db.groupmember.create(data=group_member)

    # Setup expenses
    expenses = json.loads((seeds_dir / "expenses.json").read_text())
    for expense in expenses:
        db.expense.create(data=expense)

    # Setup expense members
    expense_members = json.loads((seeds_dir / "expense_members.json").read_text())
    for expense_member in expense_members:
        db.expensemember.create(data=expense_member)


if __name__ == "__main__":
    delete_db()
    register_prisma()
    seed_db()
