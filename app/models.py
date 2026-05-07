import hashlib
import bleach
from . import db, login_manager
from sqlalchemy import ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, DynamicMapped
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from datetime import datetime, UTC
from markdown import markdown


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
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    confirmed: Mapped[bool] = mapped_column(default=False)
    name: Mapped[str | None] = mapped_column()
    location: Mapped[str | None] = mapped_column()
    about_me: Mapped[str | None] = mapped_column(Text)
    member_since: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    avatar_hash: Mapped[str | None] = mapped_column()
    posts: DynamicMapped["Post"] = relationship(back_populates="author", lazy="dynamic")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        if self.role is None:
            if self.email == current_app.config["FLASKY_ADMIN"]:
                self.role = Role.query.filter_by(name="Administrator").first()

            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self) -> None:
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self) -> str:
        s = Serializer(current_app.config["SECRET_KEY"])

        return s.dumps({"confirm": self.id})

    def confirm(self, token, expiration=3600) -> bool:
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

    def generate_reset_token(self) -> str:
        s = Serializer(current_app.config["SECRET_KEY"])

        return s.dumps({"reset": self.id})

    @staticmethod
    def reset_password(token: str, new_password: str, expiration=3600) -> bool:
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

    def generate_email_change_token(self, new_email: str) -> str:
        s = Serializer(current_app.config["SECRET_KEY"])

        return s.dumps({"change_email": self.id, "new_email": new_email})

    def change_email(self, token: str, expiration=3600) -> bool:
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
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)

        return True

    def can(self, perm: int) -> bool:
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self) -> bool:
        return self.can(Permission.ADMIN)

    def ping(self) -> None:
        self.last_seen = datetime.now(UTC)
        db.session.add(self)
        db.session.commit()

    def gravatar_hash(self) -> str:
        return hashlib.md5(self.email.lower().encode("utf-8")).hexdigest()

    def gravatar(self, size: int = 100, default: str = "identicon", rating: str = "g") -> str:
        url: str = "https://secure.gravatar.com/avatar"
        hash_avatar: str = self.avatar_hash or self.gravatar_hash()

        return f"{url}/{hash_avatar}?s={size}&d={default}&r={rating}'."

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


class Post(db.Model):

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str | None] = mapped_column(Text)
    body_html: Mapped[str | None] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True, default=lambda: datetime.now(UTC))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")

    @staticmethod
    def on_changed_body(target, value, old_value, initiator) -> None:
        allowed_tags: list[str] = [
            "a", "abbr", "acronym", "b", "blockquote", "code",
            "em", "i", "li", "ol", "pre", "strong", "ul",
            "h1", "h2", "h3", "p"
        ]

        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format="html"),
            tags=allowed_tags, strip=True))

db.event.listen(Post.body, "set", Post.on_changed_body)