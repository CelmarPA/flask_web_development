from . import db, login_manager
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DynamicMapped
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app



class Role(db.Model):

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    users: DynamicMapped[list["User"]] = relationship(backref="role", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Role {self.name!r}>"


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)

    confirmed: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"<User {self.username!r}>"

    @property
    def password(self) -> None:
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])

        return s.dumps({"confirm": self.id})

    def confirm(self, token, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"])

        try:
            data = s.loads(token, max_age=expiration)

        except Exception as e:
            _e = e
            return False

        if data.get("confirm") != self.id:
            return False

        self.confirmed = True
        db.session.add(self)

        return True

    def generate_reset_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])

        return s.dumps({"reset": self.id})

    @staticmethod
    def reset_password(token: str, new_password: str, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"])

        try:
            data = s.loads(token, max_age=expiration)

        except Exception as e:
            _e = e
            return False

        user = db.session.get(User, data.get("reset"))

        if user is None:
            return False

        user.password = new_password
        db.session.add(user)

        return True

@login_manager.user_loader
def load_user(user_id) -> User |  None:
    return db.session.get(User, int(user_id))
