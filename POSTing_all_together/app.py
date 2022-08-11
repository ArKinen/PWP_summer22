from flask import Flask, request, json, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event
from werkzeug.exceptions import HTTPException, NotFound, UnsupportedMediaType, BadRequest, Conflict
from flask_restful import Resource, Api
from werkzeug.routing import BaseConverter
#from flask_caching import Cache
from jsonschema import validate, ValidationError, draft7_format_checker
import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#app.config["CACHE_TYPE"] = "FileSystemCache"
#app.config["CACHE_DIR"] = "cache"
db = SQLAlchemy(app)
api = Api(app)
#cache = Cache(app)

deployments = db.Table("deployments",
                       db.Column("deployment_id", db.Integer, db.ForeignKey("deployment.id"), primary_key=True),
                       db.Column("sensor_id", db.Integer, db.ForeignKey("sensor.id"), primary_key=True)
                       )

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    description = db.Column(db.String(256), nullable=True)

    sensor = db.relationship("Sensor", back_populates="location", uselist=False)


class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(128), nullable=False)

    sensors = db.relationship("Sensor", secondary=deployments, back_populates="deployments")


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    model = db.Column(db.String(128), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), unique=True)

    location = db.relationship("Location", back_populates="sensor")
    measurements = db.relationship("Measurement", back_populates="sensor")
    deployments = db.relationship("Deployment", secondary=deployments, back_populates="sensors")

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["name", "model"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Sensor's unique name",
            "type": "string"
        }
        props["model"] = {
            "description": "Name of the sensor's model",
            "type": "string"
        }
        props["id"] = {
            "description": "Sensor id number",
            "type": "integer"
        }
        props["location_id"] = {
            "description": "Sensor location id number",
            "type": "integer"
        }
        return schema


class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    sensor = db.relationship("Sensor", back_populates="measurements")

    def deserialize(self, doc):
        print()
        self.time = datetime.date.fromisoformat(doc["time"])
        self.value = doc["value"]
        self.sensor = doc.get("sensor")

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["time", "value"]
        }
        props = schema["properties"] = {}
        props["time"] = {
            "description": "Time the sensor measured the value",
            "type": "string"
        }
        props["value"] = {
            "description": "Measurement result as a float",
            "type": "string"
        }
        props["id"] = {
            "description": "Measurement id number",
            "type": "integer"
        }
        props["sensor_id"] = {
            "description": "Sensor's id number",
            "type": "integer"
        }
        return schema


db.create_all()


class SensorCollection(Resource):

    @staticmethod
    def get():
        all_sensors = Sensor().query.all()

        array_of_sensors = []

        for [sensor_count, _] in enumerate(all_sensors):
            sensor_dict = {
                'name': all_sensors[sensor_count].name,
                'model': all_sensors[sensor_count].model
            }
            array_of_sensors.append(sensor_dict)

        return array_of_sensors, 200

    @staticmethod
    def post():
        try:
            sensor = Sensor(
                name=request.json["name"],
                model=request.json["model"]
            )
            db.session.add(sensor)
            db.session.commit()

            return Response(status=201, content_type='application/json')

        except (KeyError, ValueError):
            return "Attributes must be numbers", 400
        except IntegrityError:
            return "Name already exists", 409
        except (TypeError, OverflowError):
            return "Request content type must be JSON", 415


class SensorItem(Resource):

    def get(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            raise NotFound
        return Response(status=501)

    def put(self: Sensor):
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Sensor.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        self.deserialize(request.json)
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                409,
                description="Sensor with name '{name}' already exists.".format(
                    **request.json
                )
            )
        return Response(status=204)


class SensorConverter(BaseConverter):
    def to_python(self, sensor_name):
        db_sensor = Sensor.query.filter_by(name=sensor_name).first()
        if db_sensor is None:
            raise NotFound
        return db_sensor

    def to_url(self, db_sensor):
        return db_sensor.name


class MeasurementCollection(Resource):

    #def page_key(*args, **kwargs):
    #    page = request.args.get("page", 0)
    #    return request.path + f"[page_{page}]"
    #
    #PAGE_SIZE = 50
    #
    #@cache.cached(timeout=None, make_cache_key=page_key)
    #def get(self, sensor):
    #    db_sensor = Sensor.query.filter_by(name=sensor).first()
    #    if db_sensor is None:
    #        raise NotFound
    #    page = request.args.get("page", 0)
    #    remaining = Measurement.query.filter_by(
    #        sensor=db_sensor
    #    ).order_by("time").offset(page * self.PAGE_SIZE)
    #    body = {
    #        "sensor": db_sensor.name,
    #        "measurements": []
    #    }
    #    for meas in remaining.limit(self.PAGE_SIZE):
    #        body["measurements"].append(
    #            {
    #                "value": meas.value,
    #                "time": meas.time.isoformat()
    #            }
    #        )
    #    return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self, sensor):
        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, Meas.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))
        sensor.measurements.append(request.json)
        db.session.add(sensor)
        db.session.commit()
        return 201


class MeasurementItem(Resource):

    def delete(self, sensor, measurement):
        pass


class MeasurementConverter(BaseConverter):
    def to_python(self: Measurement, sensor_id_value):
        db_measurement = self.query.filter_by(sensor_id=sensor_id_value).first()
        if db_measurement is None:
            raise NotFound
        return db_measurement

    def to_url(self, db_measurement: Measurement):
        return db_measurement.name


api.add_resource(SensorCollection, "/api/sensors/")
app.url_map.converters["sensor"] = SensorConverter
api.add_resource(SensorItem, "/api/sensors/<sensor:sensor>/")

api.add_resource(MeasurementCollection, "/api/sensors/<sensor:sensor>/measurements/")
app.url_map.converters["measurement"] = MeasurementConverter
api.add_resource(MeasurementItem, "/api/sensors/<sensor:sensor>/measurements/<measurement:measurement>/")


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
