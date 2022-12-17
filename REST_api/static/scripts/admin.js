const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr;
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

function recipeRow(item) {

    let ingredient_link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderIngredient)'>show</a>";


    return "<tr><td>" + item.title +
            "</td><td>" + item.course +
            "</td><td>" + item.ingredient +
            "</td><td>" + ingredient_link +"</td></tr>";
}

function ingredientRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href + "'/a>";

    return "<tr><td>" + item.name +
            "</td><td>" + item.amount +
            "</td><td>" + item.compartment_id +
            "</td><td>" + link + "</td></tr>";
}

function appendRecipeRow(body) {
    $(".resulttable tbody").append(recipeRow(body));
}

function appendIngredientRow(body) {
    $(".resulttable tbody").append(ingredientRow(body));
}

function getSubmittedRecipe(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendRecipeRow);
    }
}

function getSubmittedIngredient(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendIngredientRow);
    }
}

function submitRecipe(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.title = $("input[name='title']").val();
    data.course = $("input[name='course']").val();
    data.ingredient = $("input[name='ingredient']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedRecipe);
}

function submitIngredient(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.name = $("input[name='name']").val();
    data.amount = $("input[name='amount']").val();
    data.compartment = $("input[name='compartment']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedIngredient);
}



function renderRecipes(body) {
    $("div.navigation").empty();
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Title</th><th>Course</th><th>Ingredient</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(recipeRow(item));
    });
    renderRecipeForm(body["@controls"]["recipe:add-recipe"]);
}

function renderRecipeForm(ctrl) {
    let form = $("<form>");
    let title = ctrl.schema.properties.title;
    let course = ctrl.schema.properties.course;
    let ingredient = ctrl.schema.properties.ingredient;

    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitRecipe);
    form.append("<label>" + title.description + "</label>");
    form.append("<input type='text' name='title'>");
    form.append("<label>" + course.description + "</label>");
    form.append("<input type='text' name='course'>");
    form.append("<label>" + ingredient.description + "</label>");
    form.append("<input type='text' name='ingredient'>");

    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function renderIngredient(body) {

    $("div.navigation")
        .html(
        "<a href='" +
        body["@controls"]["ingredient:ingredients"].href +
        "' onClick='followLink(event, this, renderIngredients)'>Ingredients</a>"
        )

    $("div.tablecontrols").empty()

    $(".resulttable thead").html(
        "<tr><th>Name</th><th>Amount</th><th>Compartment</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();

    body.items.forEach(function (item) {
        tbody.append(ingredientRow(item));
    });
}

function renderIngredients(body) {

    $("div.navigation")
        .html(
        "<a href='" +
        body["@controls"]["up"].href +
        "' onClick='followLink(event, this, renderRecipes)'>Collection</a>"
        )

    //$("div.navigation").empty();
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Add ingredient</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(ingredientRow(item));
    });
    renderIngredientForm(body["@controls"]["ingredients:add-ingredient"]);
}


function renderIngredientForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let amount  =ctrl.schema.properties.amount;
    let compartments = ctrl.schema.properties.compartments;

    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitIngredient);
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + amount.description + "</label>");
    form.append("<input type='text' name='amount'>");
    form.append("<label>" + compartments.description + "</label>");
    form.append("<input type='text' name='compartment'>");

    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

$(document).ready(function () {
    getResource("http://localhost:5000/api/recipes/", renderRecipes);
    //getResource("http://localhost:5000/api/ingredients/", renderIngredients);
});