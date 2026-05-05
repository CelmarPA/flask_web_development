from . import db, login_manager
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DynamicMapped
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app


class Permission:
    FOLLOW: int = 1
    COMMENT: int = 2
    WRITE: int = 4
    MODERATE: int = 8
    ADMIN: int = 16


class Role(db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    default: Mapped[bool] = mapped_column(default=False, index=True)
    permissions: Mapped[int] = mapped_column()

    users: DynamicMapped[list["User"]] = relationship(backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles: dict[str,list[int]] = {
            "User": [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            "Moderator": [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            "Administrator": [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }

        default_role = "User"

        for r in roles:
            role = Role.query.filter_by(name=r).first()

            if role is None:
                role = Role(name=r)

            role.reset_permissions()

            for perm in roles[r]:
                role.add_permission(perm)

            role.default = (role.name == default_role)

            db.session.add(role)

        db.session.commit()

    def add_permission(self, perm: int):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm: int):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)

    confirmed: Mapped[bool] = mapped_column(default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.role is None:
            if self.email == current_app.config["FLASKY_ADMIN"]:
                self.role = Role.query.filter_by(name="Administrator").first()

            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

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

    def generate_email_change_token(self, new_email: str):
        s = Serializer(current_app.config["SECRET_KEY"])

        return s.dumps({"change_email": self.id, "new_email": new_email})

    def change_email(self, token: str, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"])

        try:
            data = s.loads(token, max_age=expiration)

        except Exception as e:
            _e = e
            return False

        if data.get("change_email") != self.id:
            return False

        new_email = data.get("new_email")

        if new_email is None:
            return False

        if User.query.filter_by(email=new_email).first() is not None:
            return False

        self.email = new_email
        db.session.add(self)

        return True

    def can(self, perm: int):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def __repr__(self) -> str:
        return f"<User {self.username!r}>"


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id) -> User |  None:
    return db.session.get(User, int(user_id))
