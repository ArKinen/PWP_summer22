from flask import Flask

app = Flask("hello")


@app.route("/")
def index():
    return "Welcome to the site"


@app.route("/add/<float:number_1>/<float:number_2>/")
def plus(number_1, number_2):
    return "{}".format(number_1 + number_2)


@app.route("/sub/<float:number_1>/<float:number_2>/")
def minus(number_1, number_2):
    return "{}".format(number_1 - number_2)


@app.route("/mul/<float:number_1>/<float:number_2>/")
def mult(number_1, number_2):
    return "{}".format(number_1 * number_2)


@app.route("/div/<float:number_1>/<float:number_2>/")
def div(number_1, number_2):
    if number_2 == 0.0:
        result = "NaN"
    else:
        result = number_1 / number_2
    return "{}".format(result)
