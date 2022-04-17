"""Recipe model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, CustomRecipe, SavedRecipe, Collection, CollectionRecipes

os.environ['DATABASE_URL'] = "postgresql:///cook-test"

from app import app

db.create_all()

class RecipeModelTestCase(TestCase):
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


    def test_custom_recipe_model(self):

        recipe = CustomRecipe(
            title="My Ultimate Vanilla Pudding",
            ingredients="ing1, ing2, ing3",
            instructions="step1, step2, step3",
            time=20,
            servings=2,
            rating=None,
            notes=None,
            image_url=None,
            collection=None,
            made=False,
            user_id=self.testuser1.id
        )

        db.session.add(recipe)
        db.session.commit()

        self.assertEqual(self.testuser1.custom_recipes[0].id, 1)
        self.assertEqual(self.testuser1.custom_recipes[0].title, "My Ultimate Vanilla Pudding")
        self.assertEqual(self.testuser1.custom_recipes[0].servings, 2)
        self.assertEqual(self.testuser1.custom_recipes[0].user_id, self.testuser1.id)


    def test_saved_recipe_model(self):

        recipe1 = SavedRecipe(
            recipe_id=101,
            title="Chicken Penne Pasta",
            rating=None,
            notes=None,
            image_url=None,
            made=False,
            user_id=self.testuser1.id
        )

        recipe2 = SavedRecipe(
            recipe_id=102,
            title="Mac and Cheese",
            rating=None,
            notes=None,
            image_url=None,
            made=False,
            user_id=self.testuser1.id
        )

        db.session.add_all([recipe1, recipe2])
        db.session.commit()

        self.assertEqual(self.testuser1.saved_recipes[0].recipe_id, 101)
        self.assertEqual(self.testuser1.saved_recipes[0].title, "Chicken Penne Pasta")
        self.assertEqual(self.testuser1.saved_recipes[0].rating, "Not rated yet")
        self.assertEqual(self.testuser1.saved_recipes[1].recipe_id, 102)
        self.assertEqual(self.testuser1.saved_recipes[1].made, False)
        self.assertEqual(self.testuser1.saved_recipes[1].user_id, self.testuser1.id)




