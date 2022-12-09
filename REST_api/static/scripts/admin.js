const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
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

function renderRecipe(body) {
    $("div.navigation")
        .html(
        "<a href='" +
        body["@controls"]["recipe:recipes"].href +
        "' onClick='followLink(event, this, renderRecipes)'>Collection</a>"
        )

    $("div.tablecontrols").empty() //ARKI

    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    let item = body["items"][0]
    let item_self = item["@controls"].self
    //console.log("item" + item.toString())
    //console.log("item_self" + item_self.toString())
    //console.log("edit" + item_self["@controls"].edit.toString())
    //renderRecipeForm(item["@controls"].self);
    //$("input[name='title']").val(body.title);
    //$("input[name='course']").val(body.course);
   // $("form input[type='submit']").before(
     //   "<label>Location</label>" +
       // "<input type='text' name='location' value='" +
      //  body.location + "' readonly>"
   // );
}
function renderIngredients(body) {

    $("div.form").empty();
    $(".resulttable thead").html(
"<tr><th>Name</th><th>Amount</th></tr>"
    );

    $("div.navigation")
        .html("<a href='" + body["@controls"].self.href +
        "' onClick='followLink(event, this, renderIngredients)'> Ingredients</a>" + "<br>"
        )

    let val = $("div.tablecontrols").empty()


    let tbody = $(".resulttable tbody");
    tbody.empty();
    getResource(body["@controls"].self.href)
    body.items.forEach(function (item) {
        tbody.append("<tr><td>" + item.time +
            "</td><td>" + item.value +
            "</td></tr>");
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
    //renderRecipeForm(body["@controls"]["recipe:add-recipe"]);
}

function renderRecipeForm(ctrl) {
    let form = $("<form>");
    let title = ctrl.schema.properties.title;
  let course = ctrl.schema.properties.course;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitSensor);
    form.append("<label>" + title.description + "</label>");
    form.append("<input type='text' name='title'>");
    form.append("<label>" + course.description + "</label>");
    form.append("<input type='text' name='course'>");
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

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

$(document).ready(function () {
    getResource("http://localhost:5000/api/recipes/", renderRecipes);
});
