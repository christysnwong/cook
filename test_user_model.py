"""User model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, CustomRecipe, SavedRecipe, Collection, CollectionRecipes

os.environ['DATABASE_URL'] = "postgres:///cook-test"

from app import app

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # db.drop_all()
        # db.create_all()
        User.query.delete()

        testuser1 = User.signup(username="testuser1",
                                password="testuser1",
                                email="testuser1@test.com",
                                first_name="User1",
                                last_name="Test",
                                measures=None,
                                exp=None,
                                title=None)

        testuser2 = User.signup(username="testuser2",
                                password="testuser2",
                                email="testuser2@test.com",
                                first_name="User2",
                                last_name="Test",
                                measures=None,
                                exp=None,
                                title=None)

        testuser3 = User.signup(username="testuser3",
                        password="testuser3",
                        email="testuser3@test.com",
                        first_name="User3",
                        last_name="Test",
                        measures=None,
                        exp=None,
                        title=None)

        db.session.commit()

        # testuser1 = User.query.get(1)
        # testuser2 = User.query.get(2)
        # testuser3 = User.query.get(3)
        db.session.refresh(testuser1)
        db.session.refresh(testuser2)
        db.session.refresh(testuser3)

        self.testuser1 = testuser1
        self.testuser2 = testuser2
        self.testuser3 = testuser3

        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()



    def test_user_model(self):
        """Does basic model work?"""

        testuser = User(username="testuser",
                        password="testuser",
                        email="testuser@test.com",
                        first_name="User",
                        last_name="Test",
                        measures=None,
                        exp=None,
                        title=None)


        db.session.add(testuser)
        db.session.commit()

        self.assertEqual(len(testuser.custom_recipes), 0)
        self.assertEqual(len(testuser.saved_recipes), 0)
        self.assertEqual(len(testuser.collections), 0)

    
        
    def test_valid_signup(self):
        testuser4 = User.signup(username="testuser4",
                        password="testuser4",
                        email="testuser4@test.com",
                        first_name="User4",
                        last_name="Test",
                        measures=None,
                        exp=None,
                        title=None)

        db.session.commit()

        # testuser4 = User.query.get(4)
        db.session.refresh(testuser4)

        self.assertIsNotNone(testuser4)
        self.assertEqual(testuser4.username, "testuser4")
        self.assertEqual(testuser4.email, "testuser4@test.com")
        self.assertNotEqual(testuser4.password, "testuser4")
        self.assertTrue(testuser4.password.startswith("$2b$"))


    def test_invalid_signup_username(self):
        testuser0 = User.signup(username=None,
                        password="testuser0",
                        email="testuser0@test.com",
                        first_name="User0",
                        last_name="Test",
                        measures=None,
                        exp=None,
                        title=None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_signup_email(self):
        testuser0 = User.signup(username="testuser0",
                        password="testuser0",
                        email=None,
                        first_name="User0",
                        last_name="Test",
                        measures=None,
                        exp=None,
                        title=None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_signup_password(self):

        with self.assertRaises(ValueError) as context:
            User.signup("testuser0", "", "testuser0@test.com", "User0", "Test", None, None, None)

        with self.assertRaises(ValueError) as context:
            User.signup("testuser0", None, "testuser0@test.com", "User0", "Test", None, None, None)

    def test_valid_authen(self):
        user = User.authenticate(self.testuser1.username, "testuser1")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.testuser1.id)

    def test_invalid_authen(self):
        self.assertFalse(User.authenticate("abcde", "testuser1"))
        self.assertFalse(User.authenticate(self.testuser1.username, "abcde"))