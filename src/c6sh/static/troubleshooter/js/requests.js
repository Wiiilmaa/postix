$(function () {
    var title = $("title").text();
    window.setInterval(function () {
        if ($(".has-request").length) {
            $(".has-request").toggleClass("list-group-item-danger");
            $(".has-request").toggleClass("list-group-item-warning");
            if ($("title").text().indexOf("!")) {
                $("title").text("!!! " + title + " !!!");
            } else {
                $("title").text("... " + title + " ...");
            }
        }
    }, 400);
    if (!$(".has-request").length) {
        var intv = window.setInterval(function () {
            $.getJSON("/troubleshooter/session/check_requests", function (data) {
                $("#nav-sessions").toggleClass("has-request", data.has_requests);
                if (data.has_requests) {
                    window.clearInterval(intv);
                }
            });
        }, 1000);
    }
});
