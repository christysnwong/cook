"""User View tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, connect_db, User, CustomRecipe, SavedRecipe, Collection, CollectionRecipes

os.environ['DATABASE_URL'] = "postgres:///cook-test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

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

        testuser1 = User.query.get(1)
        testuser2 = User.query.get(2)
        testuser3 = User.query.get(3)

        self.testuser1 = testuser1
        self.testuser2 = testuser2
        self.testuser3 = testuser3

        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()

    def test_user_signup_invalid(self):
        with self.client as c:

            data = {"username":"testuser4",
                    "password":"testuser4",
                    "email":"testuser1@test.com",
                    "first_name":"User4",
                    "last_name":"Test"}

            resp = c.post(f"/signup", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Username or Email Address is already in use', str(resp.data))

    def test_user_signup(self):
        with self.client as c:

            data = {"username":"testuser4",
                    "password":"testuser4",
                    "email":"testuser4@test.com",
                    "first_name":"User4",
                    "last_name":"Test"}

            resp = c.post(f"/signup", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are successfully registered!', str(resp.data))                  

    
    def test_show_anon_homepage(self):
        with self.client as c:

            resp = c.get("/")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome to Cooking Master!', str(resp.data))


    def test_user_login(self):
        with self.client as c:

            data = {"username":"testuser1",
                    "password":"testuser1"}

            resp = c.post(f"/login", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Hello, testuser1!', str(resp.data))

    def test_user_login_invalid(self):
        with self.client as c:

            data = {"username":"testuser1",
                    "password":"testuser2"}

            resp = c.post(f"/login", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid credentials.', str(resp.data))


    def test_user_show_homepage(self):
        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.get("/")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Saved Recipes', str(resp.data))
            self.assertIn("You don\\\'t have any saved recipes at the moment.", str(resp.data))
            self.assertIn('Own Recipes', str(resp.data))
            self.assertIn("You haven\\\'t created any own recipes at the moment.", str(resp.data))

    

    def test_user_show_profile(self):
        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.get(f"/users/{self.testuser1.id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("testuser1", str(resp.data))
            self.assertIn("testuser1@test.com", str(resp.data))
            self.assertIn("User1 Test", str(resp.data))
            self.assertIn("Newbie", str(resp.data))
            self.assertIn("US", str(resp.data))

    def test_user_show_edit_form(self):
        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.get(f"/users/{self.testuser1.id}/edit")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit User", str(resp.data))

    def test_user_edit_profile(self):
        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"username":"testuser1",
                    "email":"testuser1@test.com",
                    "first_name":"User1",
                    "last_name":"Test",
                    "measures":"Metric"}

            resp = c.post(f"/users/{self.testuser1.id}/edit", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Metric', str(resp.data))

    def test_user_edit_profile_invalid(self):
        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"username":"testuser2",
                    "email":"testuser1@test.com",
                    "first_name":"User1",
                    "last_name":"Test",
                    "measures":"US"}

            resp = c.post(f"/users/{self.testuser1.id}/edit", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Username or Email Address is already in use', str(resp.data))


    def test_user_delete(self):
        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser3.id

            resp = c.post(f"/users/{self.testuser3.id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This account is successfully deleted.', str(resp.data))
     
   