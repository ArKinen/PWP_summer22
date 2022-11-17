import click
from flask import Flask, request, json
from flask.cli import with_appcontext
from sqlalchemy.engine import Engine
from sqlalchemy import event
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

recipes = db.Table("recipes",
                   db.Column("recipe_id", db.Integer, db.ForeignKey("recipe.id"), primary_key=True),
                   db.Column("compartment_id", db.Integer, db.ForeignKey("compartment.id"), primary_key=True))


# db.Column("recipeCategory_id", db.Integer, db.ForeignKey("recipecategory.id"), primary_key=True))

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class RecipeCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_type = db.Column(db.String(32), nullable=False, unique=True)


# recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), unique=True)
#  recipes = db.relationship("Recipe", secondary=recipes, back_populates="recipeCategory")


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(16), nullable=False, unique=True)
    ingredient = db.Column(db.String(160), nullable=False, unique=True)
    compartments = db.relationship("Compartment", secondary=recipes, back_populates="recipes")


# course = db.relationship("RecipeCategory", back_populates="recipes")
#  course_id = db.Column(db.Integer, db.ForeignKey("course.id"), unique=True)


class Compartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    location = db.relationship("Location", back_populates="compartments")
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), unique=True)
    ingredients = db.relationship("Ingredient", back_populates="compartments")
    recipes = db.relationship("Recipe", secondary=recipes, back_populates="compartments")


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    amount = db.Column(db.Integer, nullable=True)
    compartment_id = db.Column(db.Integer, db.ForeignKey("compartment.id"), unique=False)
    compartments = db.relationship("Compartment", back_populates="ingredients")


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    compartments = db.relationship("Compartment", back_populates="location")


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()


@click.command("roll")
@with_appcontext
def rollback_db_command():
    db.session.rollback()


@click.command("testgen")
@with_appcontext
def generate_test_data():
    db.session.rollback()
    all_recipes = ["Mac and Cheese", "Chicken and Potatoes", "Rice and Kebab"]
    compartments = ["Veggies", "Meat", "Mixed", "Add-ons"]
    ingredients_veggies = ["Cucumber", "Salad", "Tomato", "Paprika"]
    ingredients_mixed = ["Mashed Potatoes", "Rice"]
    ingredients_add_ons = ["Ketchup"]
    ingredients_meat = ["Chicken leg", "Minced meat", "Kebab"]
    locations = ["Fridge", "Freezer"]
    recipe_categories = ["Starters", "Main", "Dessert"]
    recipe_ingredients = ingredients_veggies + ingredients_meat + ingredients_mixed + ingredients_add_ons

    input_recipe_category(recipe_categories)
    input_location(locations)
    input_recipe(recipe_ingredients, all_recipes)
    input_compartment(compartments)
    input_ingredient(recipe_ingredients)


def input_recipe_category(_recipe_categories):
    for count, category in enumerate(_recipe_categories):
        category_model = RecipeCategory(
            course_type= str(category)
        )
        db.session.add(category_model)
        db.session.commit()


def input_location(_location):
    for count, location_name in enumerate(_location):
        location_model = Location(
            name=str(location_name)
        )
        db.session.add(location_model)
        db.session.commit()


def input_recipe(recipe_ingredients, _all_recipes):
    for recipe in range(0, len(_all_recipes)):
        used_recipe_ingredients = ""
        for i in range(0, 2):
            random_number = random.randint(0, (len(recipe_ingredients) - 1))
            # print(f"Join ingredient- {recipe_ingredients[random_number]} to {_all_recipes[recipe]}")
            if used_recipe_ingredients == "":
                # print(f"recipe_ingredients{recipe_ingredients[random_number]} not in {used_recipe_ingredients}")
                used_recipe_ingredients = recipe_ingredients[random_number]
            elif recipe_ingredients[random_number] not in used_recipe_ingredients:
                used_recipe_ingredients = used_recipe_ingredients + "," + recipe_ingredients[random_number]
            else:
                break

        recipe_model = Recipe(
            title=_all_recipes[recipe],
            ingredient=used_recipe_ingredients
        )
        db.session.add(recipe_model)
        db.session.commit()


def input_compartment(_compartments):
    for count, compartment in enumerate(_compartments):
        compartment_model = Compartment(
            name=str(compartment)
        )
        db.session.add(compartment_model)
        db.session.commit()


def input_ingredient(_recipe_ingredients):
    compartments_load_from_db = Compartment.query.all()
    for count, ingredient in enumerate(_recipe_ingredients):
        ingredient_model = Ingredient(
            name=str(ingredient),
            amount=random.randint(0, 9),
            compartments=compartments_load_from_db[random.randint(0, 3)]
        )
        # print(f"{ingredient_model.name} in {ingredient_model.compartments}")
        db.session.add(ingredient_model)
        db.session.commit()


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    if e.code == 405:
        response = "POST method required", e.code
    if e.code == 415:
        response = "Request content must be JSON", e.code
    return response


app.cli.add_command(init_db_command)
app.cli.add_command(generate_test_data)
app.cli.add_command(rollback_db_command)
