import unittest
import time
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission


class UserModelTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        Role.insert_roles()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self) -> None:
        u: User = User(email="john@example.com", username="john", password="cat")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self) -> None:
        u: User = User(email="john@example.com", username="john", password="cat")

        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self) -> None:
        u: User = User(email="john@example.com", username="john", password="cat")

        self.assertTrue(u.verify_password("cat"))
        self.assertFalse(u.verify_password("dog"))

    def test_password_salts_are_random(self) -> None:
        u1: User = User(email="john@example.com", username="john", password="cat")
        u2: User = User(email="susan@example.org", username="susan", password="dog")

        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self) -> None:
        u: User = User(email="john@example.com", username="john", password="cat")

        db.session.add(u)
        db.session.commit()

        token: str = u.generate_confirmation_token()

        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self) -> None:
        u1: User = User(email="john@example.com", username="john", password="cat")
        u2: User = User(email="susan@example.org", username="susan", password="dog")

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        token: str = u1.generate_confirmation_token()

        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self) -> None:
        u: User = User(email="john@example.com", username="john", password="cat")

        db.session.add(u)
        db.session.commit()

        token: str = u.generate_confirmation_token()

        time.sleep(2)

        self.assertFalse(u.confirm(token, expiration=1))

    def test_valid_reset_token(self) -> None:
        u: User = User(email="john@example.com", username="john", password="cat")

        db.session.add(u)
        db.session.commit()

        token: str = u.generate_reset_token()

        self.assertTrue(User.reset_password(token, "dog"))
        self.assertTrue(u.verify_password("dog"))

    def test_invalid_reset_token(self) -> None:
        u: User = User(email="john@example.com", username="john", password="cat")

        db.session.add(u)
        db.session.commit()

        token: str = u.generate_reset_token()

        self.assertFalse(User.reset_password(token + "a", "horse"))
        self.assertTrue(u.verify_password("cat"))

    def test_valid_email_change_token(self) -> None:
        u: User = User(email="john@example.com", username="john", password="cat")

        db.session.add(u)
        db.session.commit()

        token: str = u.generate_email_change_token("susan@example.org")

        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == "susan@example.org")

    def test_invalid_email_change_token(self) -> None:
        u1: User = User(email="john@example.com", username="john", password="cat")
        u2: User = User(email="susan@example.org", username="susan", password="dog")

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        token: str = u1.generate_email_change_token("david@example.net")

        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == "susan@example.org")

    def test_duplicate_email_change_token(self) -> None:
        u1: User = User(email="john@example.com", username="john", password="cat")
        u2: User = User(email="susan@example.org", username="susan", password="dog")

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        token: str = u2.generate_email_change_token("john@example.com")

        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == "susan@example.org")

    def test_user_role(self) -> None:
        u: User = User(email="john@example.com", username="john", password="cat")

        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_moderator_role(self) -> None:
        r: Role = Role.query.filter_by(name="Moderator").first()
        u: User = User(email="john@example.com", username="john", password="cat", role=r)

        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_administrator_role(self) -> None:
        r: Role = Role.query.filter_by(name="Administrator").first()
        u: User = User(email="john@example.com", username="john", password="cat", role=r)

        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))

    def test_anonymous_user(self) -> None:
        u: AnonymousUser = AnonymousUser()

        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))
