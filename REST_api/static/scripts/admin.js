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

function renderRecipes(body) {
    $("div.navigation").empty();
    $("div.tablecontrols").empty();
    //$(".resulttable thead").html(
    //    "<tr><th>Name</th><th>Model</th><th>Location</th><th>Actions</th></tr>"
    //);
    //let tbody = $(".resulttable tbody");
    //tbody.empty();

    //renderSensorForm(body["@controls"]["recipe:add-sensor"]);
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
