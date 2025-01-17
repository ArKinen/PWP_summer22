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

    let edit_link = "<a href='" +
                item["@controls"].edit.href +
                "' onClick='followLink(event, this, renderEditRecipes)'>edit</a>";

    let delete_link = "<a href='" +
                item["@controls"]["recipe:delete"].href +
                "' onClick='followLink(event, this, removeRecipeRow)'>delete</a>";


    return "<tr><td>" + item.title +
            "</td><td>" + item.course +
            "</td><td>" + item.ingredient +
            "</td><td>" + ingredient_link +
            "</td><td>" + edit_link +
            "</td><td>" + delete_link +
            "</td></tr>";
}

function appendRecipeRow(body) {
    $(".resulttable tbody").append(recipeRow(body));
}

function editRecipeRow(body) {
    sendData(body["@controls"].edit.href, body["@controls"].edit.method, body, handleEditRecipe)
}

function handleEditRecipe(data, status, jqxhr) {
    renderMsg("Succesful")
}

function removeRecipeRow(body) {
    sendData(body["@controls"]["recipe:delete"].href, body["@controls"]["recipe:delete"].method, body, handleDeletedRecipe)
}

function handleDeletedRecipe(data, status, jqxhr) {
    renderMsg("Succesful");
}

function getSubmittedRecipe(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendRecipeRow);
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

function renderRecipes(body) {
    $("div.navigation").empty();
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<h2>WhatShouldWeEatToday</h2>"+ "<th></th>" +
        "<tr><th>Title</th><th>Course</th><th>Ingredient</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(recipeRow(item));
    });
    renderRecipeForm(body["@controls"]["recipe:add-recipe"]);
}

function renderEditRecipes(body) {

    $("div.navigation")
        .html(
        "<a href='" +
        body["@controls"].collection.href +
        "' onClick='followLink(event, this, renderRecipes)'>Collection</a>"
        )
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th><h2>Edit recipe</h2></th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();

    renderEditRecipeForm(body["@controls"].edit);
}

function renderRecipeForm(ctrl) {
    let form = $("<form>");
    let title = ctrl.schema.properties.title;
    let course = ctrl.schema.properties.course;
    let ingredient = ctrl.schema.properties.ingredient;

    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitRecipe);

    form.append("<label>" + "<h2>Add recipe</h2>" + "</label>" + "<tr></tr>")
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

function renderEditRecipeForm(ctrl) {
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

function ingredientRow(item) {
    let delete_link = "<a href='" +
                item["@controls"]["ingredient:delete"].href +
                "' onClick='followLink(event, this, removeIngredientRow)'>delete</a>";

    let edit_link = "<a href='" +
                item["@controls"].edit.href +
                "' onClick='followLink(event, this, renderEditIngredients)'>edit</a>";

    return "<tr><td>" + item.name +
            "</td><td>" + item.amount +
            "</td><td>" + edit_link +
            "</td><td>" + delete_link + "</td></tr>";
}

function appendIngredientRow(body) {
    $(".resulttable tbody").append(ingredientRow(body));
}

function removeIngredientRow(body) {
    sendData(body["@controls"]["ingredient:delete"].href, body["@controls"]["ingredient:delete"].method, body, handleDeletedIngredient)
}

function handleDeletedIngredient(data, status, jqxhr) {
    renderMsg("Succesful");
}

function getSubmittedIngredient(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendIngredientRow);
    }
}

function handleEditSubmittedIngredient(data, status, jqxhr) {
    renderMsg("Successful");
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

function submitEditIngredient(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.name = $("input[name='name']").val();
    data.amount = $("input[name='amount']").val();
    data.compartment = $("input[name='compartment']").val();
    sendData(form.attr("action"), form.attr("method"), data, handleEditSubmittedIngredient);
}

function renderIngredient(body) {

    $("div.navigation")
        .html(
        "<a href='" +
        body["@controls"]["ingredient:ingredients"].href +
        "' onClick='followLink(event, this, renderIngredients)'>Ingredients</a>"
        )
    console.log(body)
    let title = body.title
    $("div.tablecontrols").empty()
    $("div.form").empty()
    $(".resulttable thead").html(
        "<h2>" + title + "</h2>" +
        "<tr><th>Name</th><th>Amount</th></tr>"
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

    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Name</th><th>Amount</th></tr>"
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
    let compartment = ctrl.schema.properties.compartment;

    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitIngredient);
    form.append("<label>" + "<h2>Add ingredient</h2>" + "</label>" + "<tr></tr>")
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + amount.description + "</label>");
    form.append("<input type='text' name='amount'>");
    form.append("<label>" + compartment.description + "</label>");
    form.append("<input type='text' name='compartment'>");

    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function renderEditIngredients(body) {

    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th><h2>Edit ingredient</h2></th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();

    renderEditIngredientForm(body["@controls"].edit);
}

function renderEditIngredientForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let amount  =ctrl.schema.properties.amount;
    let compartment = ctrl.schema.properties.compartment;

    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitEditIngredient);
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + amount.description + "</label>");
    form.append("<input type='text' name='amount'>");
    form.append("<label>" + compartment.description + "</label>");
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
});