import os

import click
from flask import Flask, request, json, Response
from flask.cli import with_appcontext
from flask_restful import Api, Resource
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError
from werkzeug.exceptions import HTTPException, NotFound, UnsupportedMediaType, BadRequest, Conflict
from flask_sqlalchemy import SQLAlchemy
import random
from jsonschema import validate, ValidationError

from werkzeug.routing import BaseConverter

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)

recipes = db.Table("recipes",
                   db.Column("recipe_id", db.Integer, db.ForeignKey("recipe.id"), primary_key=True),
                   db.Column("compartment_id", db.Integer, db.ForeignKey("compartment.id"), primary_key=True))


# db.Column("recipeCategory_id", db.Integer, db.ForeignKey("recipecategory.id"), primary_key=True))

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Recipecategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_type = db.Column(db.String(32), nullable=False, unique=True)
    recipes = db.relationship("Recipe", back_populates="course")
    # recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), unique=True)


# recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), unique=True)
#  recipes = db.relationship("Recipe", secondary=recipes, back_populates="recipeCategory")


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(16), nullable=False, unique=True)
    ingredient = db.Column(db.String(160), nullable=True, unique=True)
    compartments = db.relationship("Compartment", secondary=recipes, back_populates="recipes")
    course = db.relationship("Recipecategory", back_populates="recipes")
    course_id = db.Column(db.Integer, db.ForeignKey("recipecategory.id"), unique=False)

    def deserialize(self, doc):
        self.title = doc.get("title")
        self.ingredient = doc["ingredient"]
    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["title"]
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Recipe name",
            "type": "string"
        }
        return schema


class Compartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    location = db.relationship("Location", back_populates="compartments")
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), unique=False)
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


class RecipeCollection(Resource):
    def get(self):
        all_recipes = Recipe.query.all()

        array_of_recipes = []

        for [recipe_count, _] in enumerate(all_recipes):
            recipe_dict = {
                'title': all_recipes[recipe_count].title#,
                #'course': all_recipes[recipe_count].course.course_type
            }
            array_of_recipes.append(recipe_dict)

        return array_of_recipes, 200

    def post(self):
        if not request.json:
            return Response(status=415)

        try:
            validate(request.json, Recipe.json_schema())
        except ValidationError:
            return Response(status=400)

        recipe_to_db = Recipe(
            title=request.json["title"]
        )
        header_dict = {
            'Location': api.url_for(RecipeItem, recipe=recipe_to_db)
        }

        try:
            db.session.add(recipe_to_db)
            db.session.commit()
        except IntegrityError:
            return Response(status=409)

        return Response(status=201, content_type='text/html', headers=header_dict)


class RecipeConverter(BaseConverter):
    def to_python(self, recipe_name):
        db_recipe = Recipe.query.filter_by(title=recipe_name).first()
        if db_recipe is None:
            raise NotFound
        return db_recipe

    def to_url(self, db_recipe):
        return db_recipe.title


class RecipeItem(Resource):

    def get(self, recipe):
        db_recipe = Recipe.query.filter_by(title=recipe.title).first()
        db_recipe_dict = {
            'title': db_recipe.title,
            'course': db_recipe.course.course_type
        }
        if db_recipe is None:
            raise NotFound
        return db_recipe_dict, 200

    def put(self, recipe):
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Recipe.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        recipe.deserialize(request.json)

        try:
            db.session.add(recipe)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                409,
                description="Recipe with name '{title}' already exists.".format(
                    **request.json
                )
            )
        return Response(status=204)


api.add_resource(RecipeCollection, "/api/recipes/")
app.url_map.converters["recipe"] = RecipeConverter
api.add_resource(RecipeItem, "/api/recipes/<recipe:recipe>/")


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()


@click.command("reset")
@with_appcontext
def reset_db():
    try:
        os.system("del C:" + os.sep + "PWP_summer22" + os.sep + "REST_api" + os.sep + "test.db")
        print(f"reset_db - remove test.db from Mika")
    except:
        os.system(
            "del C:" + os.sep + "Users" + os.sep + "artok" + os.sep + "PycharmProjects" + os.sep + "PWP_summer22" + os.sep + "REST_api" + os.sep + "test.db")
        print(f"reset_db - remove test.db from Arto")


@click.command("testgen")
@with_appcontext
def generate_test_data():
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
    input_compartment(compartments)
    input_recipe(recipe_ingredients, all_recipes)
    input_ingredient(recipe_ingredients)


def input_recipe_category(_recipe_categories):
    for count, category in enumerate(_recipe_categories):
        category_model = Recipecategory(
            course_type=str(category)
        )
        db.session.add(category_model)
        db.session.commit()


def input_location(_location):
    for count, location_name in enumerate(_location):
        # compartments_load_from_db = Compartment.query.all()

        location_model = Location(
            name=str(location_name)  # ,
            # compartments=compartments_load_from_db[random.randint(0, 3)]
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
        compartments_load_from_db = Compartment.query.all()
        print(compartments_load_from_db)

        recipecategory_load_from_db = Recipecategory.query.all()
        print(recipecategory_load_from_db)

        recipe_model = Recipe(
            title=_all_recipes[recipe],
            ingredient=used_recipe_ingredients,
            compartments=compartments_load_from_db,
            course=recipecategory_load_from_db[random.randint(0, 2)]
        )

        filtered_recipes = recipe_model.course.query.filter_by(id=2).all()

        print(filtered_recipes[0].course_type)

        db.session.add(recipe_model)
        db.session.commit()

        print(
            f"Recipe: {recipe_model.title} {recipe_model.ingredient} {recipe_model.compartments} {recipe_model.course.course_type}")


def input_compartment(_compartments):
    location_load_from_db = Location.query.all()

    for count, compartment in enumerate(_compartments):
        compartment_model = Compartment(
            name=str(compartment),
            location=location_load_from_db[random.randint(0, 1)]
        )
        filtered_compartments = compartment_model.location.query.filter_by(id=2).all()
        print(filtered_compartments[0].name)

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

    for count, compartment in enumerate(compartments_load_from_db):
        # compartments_load_from_db[0].ingredients = Ingredient.query.filter_by(compartment_id=2).all()
        compartment.ingredients = Ingredient.query.filter_by(compartment_id=(count + 1)).all()
        # print(f"input_ingredient - compartment - {compartment.ingredients.query.all()}")

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
    if e.code == 400:
        response = "Resource not found", e.description
    if e.code == 405:
        response = "POST method required", e.code
    if e.code == 409:
        response = "Failed to commit", e.description
    if e.code == 415:
        response = "Request content must be JSON", e.code
    return response


app.cli.add_command(init_db_command)
app.cli.add_command(generate_test_data)
app.cli.add_command(reset_db)
