from flask import Flask, request, json, Response
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import BaseConverter
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)


class StorageEntry(db.Model):
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

    in_storage = db.relationship("StorageEntry", back_populates="product")

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["handle", "weight", "price"]
        }
        props = schema["properties"] = {}
        props["handle"] = {
            "description": "Name of the product",
            "type": "string"
        }
        props["weight"] = {
            "description": "Weight as a float",
            "type": "number"
        }
        props["price"] = {
            "description": "Price as a float",
            "type": "number"
        }
        return schema


db.create_all()


class ProductCollection(Resource):
    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["handle", "weight", "price"]
        }
        props = schema["properties"] = {}
        props["handle"] = {
            "description": "Time the sensor measured the value",
            "type": "string"
        }
        props["weight"] = {
            "description": "Weight as a float",
            "type": "number"
        }
        props["price"] = {
            "description": "Price as a float",
            "type": "number"
        }
        return schema

    @staticmethod
    def get():
        storage = StorageEntry().query.all()
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

    @staticmethod
    def post():
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

            header_dict = {
                'Location': api.url_for(ProductItem, handle=product)
            }
            return Response(status=201, content_type='application/json', headers=header_dict)
        except (KeyError, ValueError):
            return "Weight and price must be numbers", 400
        except IntegrityError:
            return "Handle already exists", 409
        except (TypeError, OverflowError):
            return "Request content type must be JSON", 415


class ProductItem(Resource):
    @staticmethod
    def get(handle):
        db_product = Product.query.filter_by(handle=handle).first()
        if db_product is None:
            raise NotFound
        return Response(status=501)

    @staticmethod
    def delete(handle):
        pass


class ProductConverter(BaseConverter):
    def to_python(self, product_handle):
        product = Product.query.filter_by(handle=product_handle).first()
        if product is None:
            raise NotFound
        return product

    def to_url(self, db_product):
        return db_product.handle


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.

    Note that child classes should set the *DELETE_RELATION* to the application
    specific relation name from the application namespace. The IANA standard
    does not define a link relation for deleting something.
    """

    DELETE_RELATION = ""

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.
        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.
        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.
        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.
        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md
        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

    def add_control_post(self, ctrl_name, title, href, schema):
        """
        Utility method for adding POST type controls. The control is
        constructed from the method's parameters. Method and encoding are
        fixed to "POST" and "json" respectively.

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        : param str title: human-readable title for the control
        : param dict schema: a dictionary representing a valid JSON schema
        """

        self.add_control(
            ctrl_name,
            href,
            method="POST",
            encoding="json",
            title=title,
            schema=schema
        )

    def add_control_put(self, title, href, schema):
        """
        Utility method for adding PUT type controls. The control is
        constructed from the method's parameters. Control name, method and
        encoding are fixed to "edit", "PUT" and "json" respectively.

        : param str href: target URI for the control
        : param str title: human-readable title for the control
        : param dict schema: a dictionary representing a valid JSON schema
        """

        self.add_control(
            "edit",
            href,
            method="PUT",
            encoding="json",
            title=title,
            schema=schema
        )

    def add_control_delete(self, title, href):
        """
        Utility method for adding PUT type controls. The control is
        constructed from the method's parameters. Control method is fixed to
        "DELETE", and control's name is read from the class attribute
        *DELETE_RELATION* which needs to be overridden by the child class.

        : param str href: target URI for the control
        : param str title: human-readable title for the control
        """

        self.add_control(
            "storage:delete",
            href,
            method="DELETE",
            title=title,
        )


class InventoryBuilder(MasonBuilder):

    def add_control_all_products(self):
        self.add_control("storage:products-all", api.url_for(ProductCollection))

    def add_control_delete_product(self, handle):
        self.add_control_delete("Delete this product", api.url_for(ProductItem, handle=handle))

    def add_control_add_product(self):
        self.add_control_post("storage:add-product", "Add a new product",
                              api.url_for(ProductCollection),
                              ProductCollection.json_schema())

    def add_control_edit_product(self, handle):
        self.add_control_put("Edit this product", api.url_for(ProductItem, handle=handle),
                             ProductCollection.json_schema())


api.add_resource(ProductCollection, "/api/products/")
app.url_map.converters["product"] = ProductConverter
api.add_resource(ProductItem, "/api/products/<product:handle>")


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
