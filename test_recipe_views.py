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

        collection1 = Collection(
            name="All",
            description="Contains all recipes collected on Cooking Master",
            user_id = self.testuser1.id
        )

        collection2 = Collection(
            name="Pasta",
            description=None,
            user_id = self.testuser1.id
        )

        collection3 = Collection(
            name="All",
            description="Contains all recipes collected on Cooking Master",
            user_id = self.testuser2.id
        )

        db.session.add_all([collection1, collection2, collection3])
        db.session.commit()

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


    def test_search_recipes(self):
        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.get("/recipes/search/1?q=chicken+penne")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Your Search: chicken penne', str(resp.data))
            self.assertIn('Results Found: 3', str(resp.data))
            self.assertIn('Chicken and Penne Pasta With Garlic Rosemary Sauce', str(resp.data))


    def test_user_show_recipes(self):

        recipe = SavedRecipe(
            recipe_id=637923,
            title="Chicken and Penne Pasta With Garlic Rosemary Sauce",
            rating=None,
            notes=None,
            image_url=None,
            made=False,
            user_id=self.testuser1.id
        )

        db.session.add(recipe)
        db.session.commit()

        with self.client as c:
            
            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.get("/recipes/show/saved")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Chicken and Penne Pasta', str(resp.data))

    
    def test_user_show_saved_recipe_in_details(self):

        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.get("/recipes/show/637923")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Chicken and Penne Pasta', str(resp.data))
            self.assertIn('Prep Time: 45 min', str(resp.data))
            self.assertIn('Add this to your favourite collections!', str(resp.data))
            self.assertIn('penne pasta', str(resp.data))
            self.assertIn('1. Boil pasta according to box directions.', str(resp.data))
            

    def test_user_add_remove_recipe(self):
        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"recipe_id":637923,
                    "title":"Chicken and Penne Pasta With Garlic Rosemary Sauce",
                    "image":"https://spoonacular.com/recipeImages/637923-556x370.jpg",
                    "user_id":self.testuser1.id,
                    "collections":[1, 2]}

            resp = c.post("/recipes/add/637923", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This recipe is successfully added to your collection(s)', str(resp.data))
            self.assertIn('Not rated yet', str(resp.data))
            self.assertIn('<a href="/collections/show/1" class="badge bg-warning">All</a>', str(resp.data))
            self.assertIn('<a href="/collections/show/2" class="badge bg-warning">Pasta</a>', str(resp.data))

            resp = c.get("/recipes/show/saved")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Chicken and Penne Pasta With Garlic Rosemary Sauce', str(resp.data))
            self.assertIn('Collections', str(resp.data))
            self.assertIn('All', str(resp.data))
            self.assertIn('Pasta', str(resp.data))

            resp = c.get("/collections/show/1")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('All Collection', str(resp.data))
            self.assertIn('Chicken and Penne Pasta With Garlic Rosemary Sauce', str(resp.data))

            resp = c.get("/collections/show/2")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Pasta Collection', str(resp.data))
            self.assertIn('Chicken and Penne Pasta With Garlic Rosemary Sauce', str(resp.data))

            resp = c.post("/recipes/remove/637923", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This recipe is successfully removed from your collection(s)', str(resp.data))


    def test_user_add_edit_recipe(self):
        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"recipe_id":637923,
                    "title":"Chicken and Penne Pasta With Garlic Rosemary Sauce",
                    "image":"https://spoonacular.com/recipeImages/637923-556x370.jpg",
                    "user_id":self.testuser1.id,
                    "collections":1}

            resp = c.post("/recipes/add/637923", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This recipe is successfully added to your collection(s)', str(resp.data))

            data = {"rating":"Not rated yet",
                    "notes":None,
                    "made":False,
                    "collections":[1, 2]}

            resp = c.post("/recipes/edit/637923", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('The info of this recipe is successfully editted.', str(resp.data))
            self.assertIn('Pasta', str(resp.data))


    def test_user_remove_recipe_invalid(self):
        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.post("/recipes/remove/637923", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This recipe is not in any of your collections.', str(resp.data))

    
    def test_user_create_show_own_recipe(self):

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

        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"title":"My Ultimate Vanilla Pudding",
                "ingredients":"ing1, ing2, ing3",
                "instructions":"step1, step2, step3",
                "time":20,
                "servings":2,
                "rating":"Not rated yet",
                "notes":None,
                "image_url":None,
                "collection":None,
                "made":False,
                "user_id":self.testuser1.id}

            resp = c.post("/recipes/custom/create", data=data, follow_redirects=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn('Your recipe is created!', str(resp.data))
            self.assertIn('Own Recipes', str(resp.data))
            self.assertIn('My Ultimate Vanilla Pudding', str(resp.data))


            resp = c.get("/recipes/custom/show/own")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('My Ultimate Vanilla Pudding', str(resp.data))


            resp = c.get("/recipes/custom/show/1")

            self.assertEqual(resp.status_code, 200)
            self.assertIn('My Ultimate Vanilla Pudding', str(resp.data))

    
    def test_user_edit_own_recipe(self):

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

        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            data = {"title":"My Ultimate Vanilla Pudding Version 2!",
                "ingredients":"ing1, ing2, ing3",
                "instructions":"step1, step2, step3",
                "time":20,
                "servings":2,
                "rating":"Not rated yet",
                "notes":None,
                "image_url":None,
                "collection":None,
                "made":False,
                "user_id":self.testuser1.id}

            resp = c.post("/recipes/custom/edit/1", data=data, follow_redirects=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn('Your recipe is successfully editted!', str(resp.data))
            self.assertIn('My Ultimate Vanilla Pudding Version 2!', str(resp.data))

    
    def test_user_delete_own_recipe(self):

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

        with self.client as c:

            with c.session_transaction() as session:
                session["CURR_USER"] = self.testuser1.id

            resp = c.post("/recipes/custom/delete/1", follow_redirects=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn('This customized recipe is successfully deleted', str(resp.data))
