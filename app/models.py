from . import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DynamicMapped


class Role(db.Model):

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    users: DynamicMapped[list["User"]] = relationship(backref="role", lazy="dynamic")

    def __repr__(self):
        return f"<Role {self.name!r}>"


class User(db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)

    def __repr__(self):
        return f"<User {self.username!r}>"
