# Cooking Master
[Check it out on Heroku!](https://cw-cooking-master.herokuapp.com)

#### Introduction

During the pandemic, dining options became limited due to restictions imposed on the restaurants. People had to buy take-out or learn how to cook on their own. 

The site targets home cooks who are running out of ideas or looking for new dishes to make for their meals. Users can search and add recipes to their collections.  Users will also be able to create and customize their own recipes.

Cooking Master utilizes the powerful Spoonacular API that enables site users to search and view thousands of recipes. One of the potential issues include not being able to extract information from the API as the allowable daily quota from the free plan is exceeded. 

#### Database Schema

![](db_schema.JPG)

#### Functionality

* Allows visitors to register for a user account and sign in
* Non-registered visitors can still search but can not save recipes
* Allows users to create their collections (ex. Desserts, pastas, drinks, desserts, breakfasts, etc).
* Allows users to search, save and categorize recipes to their collections 
* Allows users to create and edit their own recipes
* Allows users to delete any recipes in their collections

#### User Flow

* Visitors can search recipes but cannot save them
* Visitors can either register for an account or sign in to use all the site featurs
* Users can see their saved recipes and own recipes after they log in
* Users can search and add recipes to their collection
* Users can create their own recipes
* Users can add more collections to categorize their saved recipes

#### Tools

* API - Spoonacular
* Others - Python, Flask, PostgreSQL, SQLAlchemy, WTForms, HTML, and CSS

#### Set up

Prerequisites: Ensure that Pip, Python, PostgreSQL and git are already installed on your computer.

1. Make a new directory for this project
2. On your terminal, go to the directory that you just created
    * $ cd NAME_OF_DIRECTORY
3. Git-clone and download the files from github:
    * $ git clone https://github.com/christysnwong/cook.git
4. Create a file called apikeys.py
5. Visit [https://spoonacular.com/food-api](https://spoonacular.com/food-api) 
6. Register and get an API key
7. In apikeys.py, put in your API key as follows. Leave key2 empty.
    * key1 = 'YOUR_API_KEY_FROM_SPOONACULAR'
    * key2 = ''
8. Create a virtual environment in the project folder by typing the following command:
    * $ python3 -m venv venv
9. Go to virtual environment:
    * $ source venv/bin/activate 
10. Check the command line and ensure that it starts with (venv)
11. Install all the programs required for this project:
    * $ pip install -r requirements.txt
12. Ensure that PostgreSQL is already up and running. If not, start it up by typing
    * $ sudo service postgresql start 
13. To run the server on the local host:
    * $ flask run
14. Check out this project on your localhost IP address (typically http://localhost:3000)

#### Testing

* To run test files in the directory, type the following command on your terminal:
    * $ python3 -m unittest