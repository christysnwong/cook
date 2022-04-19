"""Recipe model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, CustomRecipe, SavedRecipe, Collection, CollectionRecipes

os.environ['DATABASE_URL'] = "postgres:///cook-test"

from app import app

db.create_all()

class CollectionModelTestCase(TestCase):
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


    

    def test_collection_model(self):
         
        collection = Collection(
            name="My Most Fav",
            description="My most favourites recipes",
            user_id=self.testuser1.id
        )

        db.session.add(collection)
        db.session.commit()

        self.assertEqual(self.testuser1.collections[0].name, "My Most Fav")
        self.assertEqual(self.testuser1.collections[0].description, "My most favourites recipes")
        self.assertEqual(self.testuser1.collections[0].user_id, self.testuser1.id)


