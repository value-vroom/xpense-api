"""This is a helper library, which seeds the database with some data"""
import json
import pathlib
import subprocess
import lorem
import app
import random
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
    cars_db = []
    for car in cars:
        cars_db.append(db.car.create(data=car))  # noqa: PERF401

    # Setup users
    users = json.loads((seeds_dir / "users.json").read_text())
    users_db = []
    for user in users:
        user["hashed_password"] = security.get_password_hash(user["password"])
        del user["password"]
        users_db.append(db.user.create(data=user))

    # Setup booking status
    booking_statuses = json.loads((seeds_dir / "booking_status.json").read_text())
    for booking_status in booking_statuses:
        db.bookingstatus.create(data=booking_status)

    # Setup bookings
    bookings = json.loads((seeds_dir / "bookings.json").read_text())
    for booking in bookings:
        db.booking.create(data=booking)

    # Setup reviews
    for car in cars_db:
        baseline = random.randint(1, 5)  # noqa: S311
        rating_sum = 0
        num_ratings = 0
        for user in users_db:
            for _ in range(5):
                rating = clamp(baseline + random.randint(-1, 1), 0, 5)  # noqa: S311
                rating_sum += rating
                num_ratings += 1
                db.review.create(
                    data={
                        "rating": rating,
                        "comment": lorem.get_sentence(count=1),
                        "car": {
                            "connect": {
                                "id": car.id,
                            },
                        },
                        "user": {
                            "connect": {
                                "username": user.username,
                            },
                        },
                    },
                )
        db.car.update(
            data={
                "rating": round(rating_sum / num_ratings, 1),
            },
            where={"id": car.id},
        )


if __name__ == "__main__":
    delete_db()
    register_prisma()
    seed_db()
