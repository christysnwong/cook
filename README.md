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
* Others - Python, Flask, SQLAlchemy, WTForms, HTML, and CSS

#### Set up

Prerequisites: Ensure that pip, python and git are already installed on your computer.

1. Make a new directory for this project
2. On your terminal, go to the directory that you just created
    * $ cd NAME_OF_DIRECTORY
3. Git-clone and download the files from github:
    * $ git clone https://github.com/christysnwong/cook.git
4. Start by creating a virtual environment in the project folder:
    * $ python3 -m venv venv
5. Go to virtual environment:
    * $ source venv/bin/activate 
6. Check the command line and ensure that it starts with (venv)
7. Install all the programs required for this project:
    * $ pip freeze > requirements.txt
8. To run the server on the local host:
    * $ flask run
9. Check out this project on your localhost IP address

#### Testing

* To run test files, type the following command on your terminal:
    * $ python3 -m unittest NAME_OF_TEST_FILE.py