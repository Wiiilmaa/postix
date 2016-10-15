var commands = {

    _info_view: function (content) {
        $("#info-view .content").html(content);
        $("#info-view").show();
    },

    '/help': function () {

        commands._info_view("<p><strong>Supported commands:</strong></p>"
            + "<dl class='dl-horizontal'>"
            + "<dt>/scanner</dt><dd>Show reset codes for the barcode scanner</dd>"
            + "</dl>");
    },

    process: function (command) {
        if (command.slice(0, 1) !== "/") {
            command = "/" + command;
        }
        console.log(typeof commands[command]);
        if (typeof commands[command] !== 'undefined') {
            commands[command]();
            return true;
        } else {
            return false;
        }
    },

    init: function () {
        $("#info-view .btn-close").mousedown(function () {
            $("#info-view").hide();
        })
    }

};
