$(function () {
    var title = $("title").text();
    if ($(".has-request").length) {
        window.setInterval(function () {
            $(".has-request").toggleClass("list-group-item-danger");
            $(".has-request").toggleClass("list-group-item-warning");
            if ($("title").text().indexOf("!")) {
                $("title").text("!!! " + title + " !!!");
            } else {
                $("title").text("... " + title + " ...");
            }
        }, 400);
    }
});
