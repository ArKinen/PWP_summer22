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
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderRecipe)'>show</a>";

    return "<tr><td>" + item.title +
            "</td><td>" + item.course +
            "</td><td>" + item.ingredient +
            "</td><td>" + link + "</td></tr>";
}

function ingredientRow(item) {
    return "<tr><td>" + item.name +
            "</td><td>" + item.amount +
            "</td><td>" + item.compartment_name +
            "</td></tr>";
}

function renderRecipe(body) {
    $("div.navigation")
        .html(
        "<a href='" +
        body["@controls"]["recipe:recipes"].href +
        "' onClick='followLink(event, this, renderRecipes)'>Collection</a>"
        )

    $("div.tablecontrols").empty() //ARKI

    $(".resulttable thead").html(
        "<tr><th>Name</th><th>Amount</th><th>Compartment</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();

    body.items.forEach(function (item) {
        tbody.append(ingredientRow(item));
    });
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
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.append("<label>" + title.description + "</label>");
    form.append("<input type='text' name='title'>");
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

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

$(document).ready(function () {
    getResource("http://localhost:5000/api/recipes/", renderRecipes);
});
