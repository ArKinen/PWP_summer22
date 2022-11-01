from flask import Flask, request, json
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class RecipeCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Compartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)


db.create_all()


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
