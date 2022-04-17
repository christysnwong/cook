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

        collection1 = Collection.query.get(1)
        collection2 = Collection.query.get(2)
        collection3 = Collection.query.get(3)

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

        collection1 = Collection.query.get(1)
        collection2 = Collection.query.get(2)
        collection3 = Collection.query.get(3)

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


    def test_user_add_collection_invalid(self):

        collection1 = Collection(name="All",
                                description="Contains all recipes collected on Cooking Master",
                                user_id=self.testuser1.id
        )

        collection2 = Collection(name="Pasta",
                                description=None,
                                user_id=self.testuser1.id
        )

        db.session.add_all([collection1, collection2])
        db.session.commit()

        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"name":"Pasta",
                    "description":None,
                    "user_id":self.testuser1}

            resp = c.post(f"/collections/new", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You have a collection that has the same name', str(resp.data))


    def test_user_show_edit_collection_form(self):

        collection1 = Collection(name="All",
                                description="Contains all recipes collected on Cooking Master",
                                user_id=self.testuser1.id
        )

        collection2 = Collection(name="Pasta",
                                description=None,
                                user_id=self.testuser1.id
        )

        db.session.add_all([collection1, collection2])
        db.session.commit()

        collection1 = Collection.query.get(1)
        collection2 = Collection.query.get(2)

        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.get(f"/collections/edit/{collection2.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Name of Collection (Ex. Pasta)", str(resp.data))


    def test_user_edit_collection(self):
        
        collection1 = Collection(name="All",
                                description="Contains all recipes collected on Cooking Master",
                                user_id=self.testuser1.id
            )

        collection2 = Collection(name="Pasta",
                                description=None,
                                user_id=self.testuser1.id
        )

        db.session.add_all([collection1, collection2])
        db.session.commit()

        collection1 = Collection.query.get(1)
        collection2 = Collection.query.get(2)

        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"name":"Pasta version 2",
                    "description":None}

            resp = c.post(f"/collections/edit/{collection2.id}", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('The name of this collection is successfully editted', str(resp.data))
            self.assertIn('Pasta version 2', str(resp.data))

    def test_user_edit_collection_invalid(self):
        
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

        collection1 = Collection.query.get(1)
        collection2 = Collection.query.get(2)
        collection3 = Collection.query.get(3)

        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"name":"Desserts version 2",
                    "description":None}

            resp = c.post(f"/collections/edit/{collection3.id}", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You have to be the owner of this recipe to edit this', str(resp.data))


    def test_user_edit_collection_invalid_no_edit(self):
        
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

        collection1 = Collection.query.get(1)
        collection2 = Collection.query.get(2)
        collection3 = Collection.query.get(3)

        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"name":"All version 2",
                    "description":None}

            resp = c.post(f"/collections/edit/{collection1.id}", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This collection cannot be editted', str(resp.data))


    def test_user_delete_collection(self):

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

        collection1 = Collection.query.get(1)
        collection2 = Collection.query.get(2)
        collection3 = Collection.query.get(3)

        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.post(f"/collections/delete/{collection2.id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This collection is successfully deleted', str(resp.data))


    def test_user_delete_collection_invalid(self):

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

        collection1 = Collection.query.get(1)
        collection2 = Collection.query.get(2)
        collection3 = Collection.query.get(3)

        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.post(f"/collections/delete/{collection3.id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This collection does not exist or cannot be accessed by you.', str(resp.data))

    def test_user_delete_collection_no_delete(self):

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

        collection1 = Collection.query.get(1)
        collection2 = Collection.query.get(2)
        collection3 = Collection.query.get(3)

        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.post(f"/collections/delete/{collection1.id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This collection cannot be deleted.', str(resp.data))