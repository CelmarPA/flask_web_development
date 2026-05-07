from random import randint

from dominate.tags import body
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post


def users(count: int = 100) -> None:
    fake: Faker = Faker()

    i: int = 0

    while i < count:
        u: User = User(email=fake.email(),
                       username=fake.user_name(),
                       password="password",
                       confirmed=True,
                       name=fake.name(),
                       location=fake.city(),
                       about_me=fake.text(),
                       member_since=fake.past_date())

        db.session.add(u)

        try:
            db.session.commit()
            i += 1

        except IntegrityError:
            db.session.rollback()


def posts(count: int = 100) -> None:
    fake: Faker = Faker()
    user_count: int = User.query.count()

    for i in range(count):
        u: User = User.query.offset(randint(0, user_count - 1)).first()
        p: Post = Post(body=fake.text(),
                       timestamp=fake.past_date(),
                       author=u)

        db.session.add(p)

    db.session.commit()