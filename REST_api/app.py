import click
from flask import Flask, request, json
from flask.cli import with_appcontext
from sqlalchemy.engine import Engine
from sqlalchemy import event
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy

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
    ingredient = db.Column(db.String(16), nullable=False, unique=True)
    compartments = db.relationship("Compartment", secondary=recipes, back_populates="recipes")


# course = db.relationship("RecipeCategory", back_populates="recipes")
#  course_id = db.Column(db.Integer, db.ForeignKey("course.id"), unique=True)


class Compartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.relationship("Location", back_populates="compartments")
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), unique=True)
    ingredients = db.relationship("Ingredient", back_populates="compartments")
    recipes = db.relationship("Recipe", secondary=recipes, back_populates="compartments")


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    amount = db.Column(db.Integer, nullable=True)
    compartment_id = db.Column(db.Integer, db.ForeignKey("compartment.id"), unique=True)
    compartments = db.relationship("Compartment", back_populates="ingredients")


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    compartments = db.relationship("Compartment", back_populates="location")


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()


@click.command("testgen")
@with_appcontext
def generate_test_data():
    r = Recipe(
        ingredient="chicken leg"
    )

    db.session.add(r)
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
