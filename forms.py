from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, TextAreaField, IntegerField, BooleanField
from wtforms.widgets import html5
from wtforms.validators import DataRequired, Email, Length, Optional, InputRequired, NumberRange


class UserForm(FlaskForm):
    """Form for adding users"""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])

class UserEditForm(FlaskForm):
    """Form for editing users"""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    measures = SelectField('Measuring Units', choices=[('US', 'US'), ('Metric', 'Metric')])


class LoginForm(FlaskForm):
    """Login form"""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class SavedRecipeEditForm(FlaskForm):
    """Form for edit rating or notes of user's favourite recipes"""

    rating = SelectField('Your Rating', choices=[('Not rated yet', 'Not rated yet'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    notes = TextAreaField('Notes - Optional', render_kw={'rows': 8})
    made = BooleanField('Did you make this dish?')

class CustomRecipeForm(FlaskForm):
    """Form for creating own recipe"""

    title = StringField('Recipe Title', validators=[InputRequired()])
    ingredients = TextAreaField('Ingredients', render_kw={'rows': 10}, validators=[InputRequired()])
    instructions = TextAreaField('Instructions', render_kw={'rows': 10}, validators=[InputRequired()])
    time = IntegerField('Prep Time (min)', widget=html5.NumberInput(min=1, max=360), validators=[NumberRange(min=1, max=360, message='Invalid Prep Time')])
    servings = IntegerField('Servings', widget=html5.NumberInput(min=1, max=20), validators=[NumberRange(min=1, max=20, message='Invalid Servings')])
    rating = SelectField('Your Rating', choices=[('Not rated yet', 'Not rated yet'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    notes = TextAreaField('Notes (Optional)', render_kw={'rows': 8})
    made = BooleanField('Did you make this dish?')
    image_url = StringField('Image URL (Optional)') 


class CollectionForm(FlaskForm):
    """Form for creating a collection"""

    name = StringField('Name of Collection (Ex. Pasta)', validators=[Length(min=1, max=20, message='Name cannot be more than 20 characters')])
    description = StringField('Description (Optional)', validators=[Length(max=55, message='Description cannot be more than 55 characters')])





