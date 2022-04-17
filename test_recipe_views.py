"""Recipe View tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, connect_db, User, CustomRecipe, SavedRecipe, Collection, CollectionRecipes

os.environ['DATABASE_URL'] = "postgresql:///cook-test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class RecipeViewTestCase(TestCase):
    """Test views for recipes and collections."""

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

        db.session.commit()

        testuser1 = User.query.get(1)
        testuser2 = User.query.get(2)

        self.testuser1 = testuser1
        self.testuser2 = testuser2

        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()

    def test_unauth_access_without_reg(self):

        with self.client as c:

            resp = c.get("/collections/show", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))

            resp = c.get("/collections/new", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))

            resp = c.get("/recipes/custom/show/own", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))

            resp = c.get("/recipes/custom/create", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))

            resp = c.get("/recipes/show/saved", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', str(resp.data))


    def test_user_show_all_collections(self):

        collection1 = Collection(name="All",
                                description="Contains all recipes collected on Cooking Master",
                                user_id=self.testuser1.id
        )

        collection2 = Collection(name="Pasta",
                                description=None,
                                user_id=self.testuser1.id
        )

        collection3 = Collection(name="Desserts",
                                description=None,
                                user_id=self.testuser2.id
        )

        db.session.add_all([collection1, collection2, collection3])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.get("/collections/show")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('My Collections', str(resp.data))
            self.assertIn('All', str(resp.data))
            self.assertIn('Contains all recipes collected on Cooking Master', str(resp.data))
            self.assertIn('Pasta', str(resp.data))
            self.assertNotIn('Desserts', str(resp.data))


    def test_user_show_collection_in_details(self):

        collection1 = Collection(name="All",
                                description="Contains all recipes collected on Cooking Master",
                                user_id=self.testuser1.id
        )

        collection2 = Collection(name="Pasta",
                                description=None,
                                user_id=self.testuser1.id
        )

        collection3 = Collection(name="Desserts",
                                description=None,
                                user_id=self.testuser2.id
        )

        db.session.add_all([collection1, collection2, collection3])
        db.session.commit()

        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id
            

            resp = c.get(f"/collections/show/{collection2.id}")

            # import pdb
            # pdb.set_trace()

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Pasta Collection', str(resp.data))
            

    def test_user_show_collection_in_details_unauth(self):
        
        collection1 = Collection(name="All",
                                description="Contains all recipes collected on Cooking Master",
                                user_id=self.testuser1.id
        )

        collection2 = Collection(name="Pasta",
                                description=None,
                                user_id=self.testuser1.id
        )

        collection3 = Collection(name="Desserts",
                                description=None,
                                user_id=self.testuser2.id
        )

        db.session.add_all([collection1, collection2, collection3])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.get(f"/collections/show/{collection3.id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This collection does not exist or cannot be accessed by you.', str(resp.data))


    def test_user_add_collection(self):
        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"name":"Dinner",
                    "description":"Dinner ideas",
                    "user_id":self.testuser1}

            resp = c.post(f"/collections/new", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This collection is successfully added', str(resp.data))
            self.assertIn('Dinner', str(resp.data))
            self.assertIn('Dinner ideas', str(resp.data))

