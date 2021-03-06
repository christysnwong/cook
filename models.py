from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """Users"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    first_name = db.Column(
        db.Text,
        nullable=False
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    measures = db.Column(
        db.Text,
        nullable=True,
        default='US'
    )

    exp = db.Column(
        db.Integer,
        nullable=True,
        default=0
    )

    title = db.Column(
        db.Text,
        nullable=True,
        default='Newbie'
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"


    custom_recipes = db.relationship('CustomRecipe', backref='user', cascade = "all,delete-orphan")
    
    saved_recipes = db.relationship('SavedRecipe', backref='user', cascade = "all,delete-orphan")
    
    collections = db.relationship('Collection', backref='user', cascade = "all,delete-orphan")


    @classmethod
    def signup(cls, username, password, email, first_name, last_name, measures, exp, title):
        """Register user with hashed password"""

        hashed = bcrypt.generate_password_hash(password)
        
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        user = User(username=username, 
            password=hashed_utf8, 
            email=email, 
            first_name=first_name, 
            last_name=last_name, 
            measures=measures,
            exp=exp, 
            title=title
        )

        db.session.add(user)

        return user


    @classmethod
    def authenticate(cls, username, password):
        """Validate username and password"""

        user = cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class CustomRecipe(db.Model):
    """Custom Recipe"""

    __tablename__ = 'custom_recipes'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    
    title = db.Column(
        db.Text,
        nullable=False
    )

    ingredients = db.Column(
        db.Text,
        nullable=False
    )

    instructions = db.Column(
        db.Text,
        nullable=False
    )

    time = db.Column(
        db.Integer,
        nullable=False
    )

    servings = db.Column(
        db.Integer,
        nullable=False
    )

    rating = db.Column(
        db.Text,
        nullable=True,
        default='Not rated yet'
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    image_url = db.Column(
        db.Text,
        nullable=True,
        default='/static/images/default.jpg'
    )

    collection = db.Column(
        db.Text,
        nullable=True,
        default='Own'
    )

    made = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    # user = db.relationship('User', backref='custom_recipes', cascade="all,delete")


class SavedRecipe(db.Model):
    """User's Saved Recipe"""

    __tablename__ = 'saved_recipes'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True

    )

    recipe_id = db.Column(
        db.Integer,
        nullable=True
    )
    
    title = db.Column(
        db.Text,
        nullable=False
    )

    rating = db.Column(
        db.Text,
        nullable=True,
        default='Not rated yet'
    )

    notes = db.Column(
        db.Text,
        nullable=True,
        default='None'
    )
    
    image_url = db.Column(
        db.Text,
        default='/static/images/default.jpg'
    )

    made = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    # user = db.relationship('User', backref='saved_recipes', cascade="all,delete")

    collections = db.relationship('Collection', 
        secondary='collection_recipes',
        order_by='Collection.name',
        backref='saved_recipes')


class Collection(db.Model):
    """Collection of Categorized Recipes"""

    __tablename__ = 'collections'

    id = db.Column(db.Integer,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(db.String(20),
        nullable=False       
    )

    description = db.Column(db.String(50),
        nullable=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    # user = db.relationship('User', backref='collections', cascade="all,delete")

    def __repr__(self):
        return f"<Collection id={self.id} name={self.name}>"


class CollectionRecipes(db.Model):
    """Mapping of Saved Recipes to a Collection"""

    __tablename__ = 'collection_recipes'

    collection_id = db.Column(db.Integer,
        db.ForeignKey('collections.id', ondelete='cascade'),
        primary_key=True
    )

    recipe_id = db.Column(db.Integer,
        db.ForeignKey('saved_recipes.id', ondelete='cascade'),
        primary_key=True    
    )


    
