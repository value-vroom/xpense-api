"""This is a helper library, which seeds the database with some data"""
import json
import pathlib
import subprocess

import app
from app.utility import security
from prisma import Prisma, get_client, register


def delete_db() -> None:
    """Delete the database"""
    database_dir = (pathlib.Path(app.__file__).parent.parent / "prisma" / "database.db").resolve()
    subprocess.run(["rm", database_dir], check=True)  # noqa: S603, S607
    subprocess.run(["prisma", "db", "push"], check=True)  # noqa: S603, S607


def register_prisma() -> None:
    """Register the Prisma client"""
    db = Prisma()
    db.connect()
    register(db)


def seed_db() -> None:
    """Seeds the database with some data"""
    db = get_client()

    # Seeds dir
    seeds_dir = pathlib.Path(app.__file__).parent.parent / "seeds"

    # Setup car brand
    car_brands = json.loads((seeds_dir / "car_brands.json").read_text())
    for car_brand in car_brands:
        db.carbrand.create(data=car_brand)

    # Setup car model
    car_models = json.loads((seeds_dir / "car_models.json").read_text())
    for car_model in car_models:
        db.carmodel.create(data=car_model)

    # Setup cars
    cars = json.loads((seeds_dir / "cars.json").read_text())
    for car in cars:
        db.car.create(data=car)

    # Setup users
    users = json.loads((seeds_dir / "users.json").read_text())
    for user in users:
        user["hashed_password"] = security.get_password_hash(user["password"])
        del user["password"]
        db.user.create(data=user)


def setup_db() -> None:
    """Seeds the database with some data"""
    delete_db()
    register_prisma()
    seed_db()


if __name__ == "__main__":
    setup_db()
