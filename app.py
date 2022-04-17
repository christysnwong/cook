import os
import requests
import math

from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError, PendingRollbackError


from forms import UserForm, UserEditForm, LoginForm, SavedRecipeEditForm, CustomRecipeForm, CollectionForm
from models import db, connect_db, User, CustomRecipe, SavedRecipe, Collection

app = Flask(__name__)

key1 = '9e055b5f64f34fdabb8c20a3a2fa1ef8'
key2 = '1078cbb8d35341d8bc2e994f794b463c'

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///cook'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.config['TESTING'] = False
connect_db(app)
# db.drop_all()
db.create_all()

##############################################################################
# User signup/login/logout routes

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if "CURR_USER" in session:
        g.user = User.query.get(session["CURR_USER"])
        
    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session["CURR_USER"] = user.id


def do_logout():
    """Logout user."""

    if "CURR_USER" in session:
        del session["CURR_USER"]



@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    """

    form = UserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                measures=None,
                exp=None,
                title=None
            )

            db.session.add(user)
            db.session.commit()

            collection = Collection(
                name = "All",
                description = "Contains all recipes collected on Cooking Master",
                user_id = user.id
            )

            db.session.add(collection)
            db.session.commit()

            flash("You are successfully registered!", 'success')


        except IntegrityError:
            flash("Username or Email Address is already in use", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    flash(f"Goodbye, {g.user.username}!", "info")
    do_logout()
    return redirect('/')


##############################################################################
# General Homepage:
    
@app.route('/')
def users_show_recipes():
    """Show user's saved and custom recipes"""

    if g.user:
        
        user = User.query.get_or_404(g.user.id)
        # recipes = user.saved_recipes + user.custom_recipes

        # saved_recipes = user.saved_recipes

        saved_recipes = SavedRecipe.query.filter(SavedRecipe.user_id == g.user.id).order_by(SavedRecipe.id.desc()).limit(8).all() or None

        custom_recipes = CustomRecipe.query.filter(CustomRecipe.user_id == g.user.id).order_by(CustomRecipe.id.desc()).limit(8).all() or None 

        collections = user.collections

        # import pdb
        # pdb.set_trace()

        return render_template('recipes/show_all.html',saved_recipes=saved_recipes, custom_recipes=custom_recipes, collections=collections)

    else:
        return render_template('home.html')

##############################################################################
# General user routes:

@app.route('/users/guide')
def show_guide():
    """Show user's guide"""

    return render_template('users/guide.html')


@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def users_profile_show(user_id):
    """Show user profile."""

    if g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user = User.query.get_or_404(user_id)

        progress = users_cal_progress(user)

        return render_template('users/profile.html', user=user, progress=progress)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def users_profile_edit(user_id):
    """Edit user profile."""

    if g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user = User.query.get_or_404(user_id)
        form = UserEditForm(obj=user)

        if form.validate_on_submit():

            try:
                user.username = form.username.data
                user.email = form.email.data
                user.first_name = form.first_name.data
                user.last_name = form.last_name.data
                user.measures = form.measures.data

                db.session.commit() 
                flash('Your profile is Editted!', 'success')
                return redirect(f'/users/{user_id}')

            except IntegrityError:
                db.session.rollback() # why need to rollback here? if signup with same username, doesn't require to rollback
                flash("Username or Email Address is already in use", 'danger')
                
        return render_template('users/profile_edit.html', user=user, form=form)


@app.route('/users/<int:user_id>/delete', methods=['GET', 'POST'])
def users_profile_delete(user_id):
    """Delete a user's profile."""

    if g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user = User.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()
        session.pop("CURR_USER")
        flash(f'This account is successfully deleted.', 'success')

        return redirect('/login')


def users_update_exp(pts):
    """update experience points"""

    user = User.query.get_or_404(g.user.id)

    user.exp = user.exp + pts

    if user.title != "Cooking Master":
        users_update_lvl(user)
    
    db.session.commit()


def users_update_lvl(user):

    if user.exp > 4 and user.exp <= 10:
        user.title = "Amateur Cook"

    if user.exp > 10 and user.exp <= 30:
        user.title = "Junior Cook"

    if user.exp > 30 and user.exp <= 60:
        user.title = "Cook"

    if user.exp > 60:
        user.title = "Cooking Master"


def users_cal_progress(user):

    if user.exp <= 4:
        progress = user.exp / 4 * 100

    if user.exp > 4 and user.exp <= 10:
        progress = (user.exp - 4) / (10 - 4) * 100

    if user.exp > 10 and user.exp <= 30:
        progress = (user.exp - 10) / (30 - 10) * 100

    if user.exp > 30 and user.exp <= 60:
        progress = (user.exp - 30) / (60 - 30) * 100

    if user.exp > 60:
        progress = 100

    return progress

##############################################################################
# API calls for Recipes

@app.route('/recipes/search/<int:pg_num>')
def search_recipes(pg_num):
    """Returns search results for recipes"""

    search = request.args.get('q')

    offset = 8 * (pg_num - 1)

    resp = requests.get('https://api.spoonacular.com/recipes/complexSearch',
        params={'apiKey': key1, 'query': search, 'offset': offset, 'number': 8})


    if 'code' in resp.json() and resp.json()['code'] == 402:

        resp = requests.get('https://api.spoonacular.com/recipes/complexSearch',
        params={'apiKey': key2, 'query': search, 'offset': offset, 'number': 8})

        if 'code' in resp.json() and resp.json()['code'] == 402:

            flash('Sorry the daily search limit has been reached. Please try again next day.', 'info')
            return redirect('/')


    if not search or not resp.json()['totalResults']:
        errors = 'Your search is invalid. Please try again.'
        return render_template('recipes/search.html', errors=errors)
    
    else:
        results = resp.json()['results']
        total_results = resp.json()['totalResults']

        total_pg = math.ceil(total_results / 8)
        curr_pg = pg_num

        return render_template('recipes/search.html', search=search, results=results, total=total_results, curr_pg=curr_pg, total_pg=total_pg)

    return render_template('recipes/search.html', search=search, results=results, total=total_results, curr_pg=curr_pg, total_pg=total_pg)

##############################################################################
# Saved & own recipes routes

@app.route('/recipes/show/saved')
def show_saved_recipes():
    """Show all of user's saved recipes"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:

        user = User.query.get_or_404(g.user.id)
        saved_recipes = SavedRecipe.query.filter(SavedRecipe.user_id == user.id).order_by(SavedRecipe.title).all() or None


        return render_template('recipes/show_all_saved.html', saved_recipes=saved_recipes)


@app.route('/recipes/show/<int:recipe_id>')
def show_recipe(recipe_id):
    """Show details of a recipe"""

    resp = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information',
        params={'apiKey': key1})

    if 'code' in resp.json() and resp.json()['code'] == 402:
       
        resp = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information',
        params={'apiKey': key2})

        if 'code' in resp.json() and resp.json()['code'] == 402:

            flash('Sorry the daily search limit has been reached. Please try again next day.', 'info')
            return redirect('/recipes/show/saved')


    title = resp.json()["title"]
    image = resp.json()["image"]
    servings = resp.json()["servings"]
    time = resp.json()["readyInMinutes"]
    ingredients = resp.json()["extendedIngredients"]
    instructions = resp.json()["analyzedInstructions"]

    if g.user:
        user_id = g.user.id
        recipe = SavedRecipe.query.filter(SavedRecipe.user_id == user_id, SavedRecipe.recipe_id == recipe_id).first()

    else:
        recipe = None

    return render_template('recipes/show_saved.html', recipe_id=recipe_id, title=title, image=image, servings=servings, time=time, ingredients=ingredients,instructions=instructions, recipe=recipe)


@app.route('/recipes/add/<int:recipe_id>', methods=['POST'])
def add_recipe(recipe_id):
    """Add recipe to user's favourites"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    title = request.form["title"]
    image = request.form["image"]

    collection_ids = [int(num) for num in request.form.getlist("collections")]
    
    if len(collection_ids) == 0:
        flash("This recipe is not added to any collections", 'warning')
        return redirect(f'/recipes/show/{recipe_id}')

   
    recipe = SavedRecipe(
        recipe_id = recipe_id,
        title = title,
        image_url = image,
        user_id = g.user.id
    )

    saved_recipe_ids = [recipe.recipe_id for recipe in g.user.saved_recipes]

    if recipe_id in saved_recipe_ids:
        flash("This recipe is already added to your collection", 'danger')

    else:
        recipe.collections = Collection.query.filter(Collection.id.in_(collection_ids)).all()
        users_update_exp(1)

        db.session.add(recipe)
        db.session.commit()
        flash('This recipe is successfully added to your collection(s)', 'success')
    
    return redirect(f'/recipes/show/{recipe_id}')


@app.route('/recipes/remove/<int:recipe_id>', methods=['GET', 'POST'])
def remove_recipe(recipe_id):
    """Remove recipe from user's favourites"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user_id = g.user.id
        recipe = SavedRecipe.query.filter(SavedRecipe.user_id == user_id, SavedRecipe.recipe_id == recipe_id).first()

        if recipe == None:
            flash(f'This recipe is not in your favourite.', 'danger')
            return redirect(f'/recipes/show/{recipe_id}')

        db.session.delete(recipe)
        db.session.commit()
        flash(f'This recipe is successfully removed from your favourite.', 'success')

        return redirect(f'/recipes/show/{recipe_id}')

@app.route('/recipes/edit/<int:recipe_id>', methods=['GET','POST'])
def edit_recipe(recipe_id):
    """Edit recipe's rating and notes from user's favourites"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    else:
        user_id = g.user.id
                
        recipe = SavedRecipe.query.filter(SavedRecipe.user_id == user_id, SavedRecipe.recipe_id == recipe_id).first()
        collections = g.user.collections

        form = SavedRecipeEditForm(obj=recipe)

        if recipe == None:
            flash(f'This recipe needs to be added to your favourite before you can edit.', 'danger')
            return redirect(f'/recipes/show/{recipe_id}')

        
        if form.validate_on_submit():
            recipe.rating = form.rating.data
            recipe.notes = form.notes.data
            recipe.made = form.made.data

            collection_ids = [int(num) for num in request.form.getlist("collections")]
            recipe.collections = Collection.query.filter(Collection.id.in_(collection_ids)).all()

            if len(recipe.collections) == 0:
                db.session.delete(recipe)
                flash(f'The info of this recipe is removed from all of your collections.', 'success')
            
            else:

                if recipe.made == True:
                    users_update_exp(5)

                flash(f'The info of this recipe is successfully editted.', 'success')

            db.session.commit()

            
            return redirect(f'/recipes/show/{recipe_id}')

        return render_template('recipes/edit_saved.html', form=form, recipe=recipe, recipe_id=recipe_id, collections=collections)


@app.route('/recipes/custom/create', methods=['GET', 'POST'])
def create_own_recipe():
    """Create own's recipe"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user_id = g.user.id

        form = CustomRecipeForm()

        if form.validate_on_submit():

            recipe = CustomRecipe(
                title = form.title.data,
                ingredients = form.ingredients.data,
                instructions = form.instructions.data,
                time = form.time.data,
                servings = form.servings.data,
                rating = form.rating.data,
                notes = form.notes.data or None,
                made = form.made.data,
                image_url = form.image_url.data or CustomRecipe.image_url.default.arg,
                user_id = user_id
            )

            if form.made.data == True:
                users_update_exp(9)
            else:
                users_update_exp(4)

            db.session.add(recipe)
            db.session.commit()

            flash(f'Your recipe is created!', 'success')
            return redirect('/recipes/custom/show/own')
        
        return render_template('recipes/create.html', form=form)

@app.route('/recipes/custom/show/own')
def show_own_recipes():
    """Show all of user's own recipes"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:

        user = User.query.get_or_404(g.user.id)
        custom_recipes = CustomRecipe.query.filter(CustomRecipe.user_id == user.id).order_by(CustomRecipe.title).all() or None

        return render_template('recipes/show_all_own.html',custom_recipes=custom_recipes)

   

@app.route('/recipes/custom/show/<int:recipe_id>')
def show_own_recipe(recipe_id):
    """Show details of own's recipe"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user_id = g.user.id
        recipe = CustomRecipe.query.filter(CustomRecipe.user_id == user_id, CustomRecipe.id == recipe_id).first()

        if recipe == None:
            flash(f'You have to be the owner of this recipe to view this', 'danger')
            return redirect('/')

        return render_template('recipes/show_custom.html', recipe=recipe)


@app.route('/recipes/custom/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_own_recipe(recipe_id):
    """Edit own's recipe"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user_id = g.user.id

        recipe = CustomRecipe.query.filter(CustomRecipe.user_id == user_id, CustomRecipe.id == recipe_id).first()
        form = CustomRecipeForm(obj=recipe)

        if recipe == None:
            flash(f'You have to be the owner of this recipe to edit this', 'danger')
            return redirect('/')

        if form.validate_on_submit():

            recipe.title = form.title.data
            recipe.ingredients = form.ingredients.data
            recipe.instructions = form.instructions.data
            recipe.time = form.time.data
            recipe.servings = form.servings.data
            recipe.rating = form.rating.data
            recipe.notes = form.notes.data or None
            recipe.made = form.made.data
            recipe.image_url = form.image_url.data or CustomRecipe.image_url.default.arg
        
            if recipe.made == True:
                users_update_exp(5)

            db.session.commit()

            flash(f'Your recipe is successfully editted!', 'success')
            return redirect(f'/recipes/custom/show/{recipe_id}')
        
        return render_template('recipes/edit_custom.html', form=form, recipe=recipe)

    

@app.route('/recipes/custom/delete/<int:recipe_id>', methods=['POST'])
def delete_own_recipe(recipe_id):
    """Delete own's recipe"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user_id = g.user.id
        recipe = CustomRecipe.query.filter(CustomRecipe.user_id == user_id, CustomRecipe.id == recipe_id).first()

        if recipe == None:
            flash(f'This recipe does not exist or cannot be accessed by you.', 'danger')
            return redirect('/')

        db.session.delete(recipe)
        db.session.commit()
        flash(f'This customized recipe is successfully deleted', 'success')

        return redirect('/')

##############################################################################
# Collection routes

@app.route('/collections/show')
def show_collections():
    """Show user's list of collections"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user = g.user
        collections = Collection.query.filter(Collection.user_id == user.id, Collection.name == 'All').all() + Collection.query.filter(Collection.user_id == user.id, Collection.name != 'All').order_by(Collection.name).all()

        return render_template('collections/show.html', collections=collections)

@app.route('/collections/show/<int:collection_id>')
def show_collection_in_details(collection_id):
    """Shows recipes in a collection"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user_id = g.user.id
        collection = Collection.query.filter(Collection.user_id == user_id, Collection.id == collection_id).first()
        recipes = collection.saved_recipes

        if collection == None:
            flash(f'This collection does not exist or cannot be accessed by you.', 'danger')
            return redirect('/collections/show')

        return render_template('collections/show_details.html', collection=collection, recipes=recipes)


@app.route('/collections/new', methods=['GET', 'POST'])
def add_collection():
    """Show a form to create a collection folder"""


    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        collections = Collection.query.filter(Collection.user_id == g.user.id).all()
        collections_names = [collection.name for collection in collections]

        form = CollectionForm()

        if len(collections) > 14:
            flash(f'Sorry you have already reached the maximum number of collection folders you can store.', 'danger')
            return redirect('/collections/show')
   
        if form.validate_on_submit():

            collection = Collection(
                name = form.name.data.capitalize(),
                description = form.description.data,
                user_id = g.user.id
            )

            if collection.name in collections_names:
                flash(f'You have a collection that has the same name "{collection.name}" already', 'warning')
                return redirect('/collections/new')

            users_update_exp(1)
            
            db.session.add(collection)
            db.session.commit()
            flash('This collection is successfully added', 'info')

            return redirect('/collections/show')

        return render_template('collections/add.html', form=form)

@app.route('/collections/edit/<int:collection_id>', methods=['GET', 'POST'])
def edit_collection(collection_id):
    """Show a form to edit a collection folder"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user_id = g.user.id
        collection = Collection.query.filter(Collection.user_id == user_id, Collection.id == collection_id).first()
        
        
        form = CollectionForm(obj=collection)

        if collection == None:
            flash(f'You have to be the owner of this recipe to edit this', 'danger')
            return redirect('/collections/show')

        if collection.name == "All":
            flash(f'This collection cannot be editted', 'danger')
            return redirect('/collections/show')


        if form.validate_on_submit():

            collection.name = form.name.data
            collection.description = form.description.data

            db.session.commit()
            flash('The name of this collection is successfully editted', 'success')

            return redirect('/collections/show')
        
        return render_template('collections/edit.html', form=form, collection=collection)


@app.route('/collections/delete/<int:collection_id>', methods=['POST'])
def delete_collection(collection_id):
    """Delete a collection"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    else:
        user_id = g.user.id
        collection = Collection.query.filter(Collection.user_id == user_id, Collection.id == collection_id).first()

        if collection == None:
            flash(f'This collection does not exist or cannot be accessed by you.', 'danger')
            return redirect('/collections/show')

        
        if collection.name == "All":
            flash(f'This collection cannot be deleted.', 'danger')
            return redirect('/collections/show')

        db.session.delete(collection)
        db.session.commit()
        flash(f'This collection is successfully deleted', 'success')

        return redirect("/collections/show")


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
