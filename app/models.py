from . import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DynamicMapped
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    users: DynamicMapped[list["User"]] = relationship(backref="role", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Role {self.name!r}>"


class User(db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)

    password_hash: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.username!r}>"

    @property
    def password(self) -> None:
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> None:
        return check_password_hash(self.password_hash, password)
