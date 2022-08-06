from flask import Flask, request, json
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)


class StorageItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    location = db.Column(db.String(64), nullable=False)

    product = db.relationship("Product", back_populates="in_storage")


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String(64), unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)

    in_storage = db.relationship("StorageItem", back_populates="product")


db.create_all()


class ProductCollection(Resource):

    def get(self):
        storage = StorageItem().query.all()
        all_products = Product().query.all()

        array_of_products = []
        for [product_count, _] in enumerate(all_products):
            product_id = all_products[product_count].id
            array_of_items_per_product = []
            for [item_count, _] in enumerate(storage):
                if storage[item_count].product_id == product_id:
                    inventory_item = [
                        storage[item_count].location,
                        storage[item_count].qty
                    ]
                    array_of_items_per_product.append(inventory_item)

            storage_dict = {
                'handle': all_products[product_count].handle,
                'weight': all_products[product_count].weight,
                'price': all_products[product_count].price,
            }
            array_of_products.append(storage_dict)

        return array_of_products, 200

    def post(self):
        try:
            handle_value = request.json["handle"]
            weight_value = float(request.json["weight"])
            price_value = float(request.json["price"])

            product = Product(
                handle=handle_value,
                weight=weight_value,
                price=price_value
            )
            db.session.add(product)
            db.session.commit()

            return "{}", 201
        except (KeyError, ValueError):
            return "Weight and price must be numbers", 400
        except IntegrityError:
            return "Handle already exists", 409
        except (TypeError, OverflowError):
            return "Request content type must be JSON", 415


api.add_resource(ProductCollection, "/api/products/")


@app.errorhandler(HTTPException)
def handle_exception(e):
    # """Return JSON instead of HTML for HTTP errors."""
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
