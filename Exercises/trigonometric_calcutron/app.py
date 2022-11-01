from flask import Flask, request
import math
import re
app = Flask("trigonometric_calcutron")


@app.route("/trig/<func>/")
def trig(func):
    unit = "radian"
    try:
        if re.match("sin|cos|tan", func) is None:
            return "Operation not found", 404
        angle = request.args.get("angle")
        unit = request.args.get("unit")
        if unit not in ("degree", "radian", None):
            return "Invalid query parameter value(s)", 400
        if unit == "degrees":
            angle = math.radians(float(angle))
        if func == "sin":
            angle = math.sin(float(angle))
        elif func == "cos":
            angle = math.cos(float(angle))
        elif func == "tan":
            angle = math.tan(float(angle))
    except (KeyError, TypeError, ValueError) as error:
        return "Invalid query parameter value(s)", 400
    return "{}".format(angle)
