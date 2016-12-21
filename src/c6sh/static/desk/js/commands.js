var commands = {

    _info_view: function (content) {
        $("#info-view .content").html(content);
        $("#info-view").show();
    },

    '/help': function () {
        commands._info_view("<p><strong>" + gettext("Supported commands:") + "</strong></p>"
            + "<dl class='dl-horizontal'>"
            + "<dt>/scanner</dt><dd>" + gettext("Show reset codes for the barcode scanner") + "</dd>"
            + "</dl>");
    },

    '/ping': function(param) {
        if (param && param.length > 5) {
            $.ajax({
                url: '/api/cashdesk/pong/',
                method: 'POST',
                dataType: 'json',
                data: JSON.stringify({
                    'pong': param
                }),
                headers: {
                    'Content-Type': 'application/json'
                },
            });
        } else {
            $.ajax({
                url: '/api/cashdesk/print-ping/',
                method: 'POST',
                dataType: 'json',
                data: '',
                headers: {
                    'Content-Type': 'application/json'
                },
            });
        }
    },

    '/scanner': function () {
        commands._info_view("<p><strong>" + gettext("Scan the following, in order:") + "</strong></p>"
            + "<p>"
            + "<img src='/static/c6sh/desk/img/scanner/honeywell01.png'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            + "<img src='/static/c6sh/desk/img/scanner/honeywell02.png'>"
            + "</p>"
            + "<p>"
            + "<img src='/static/c6sh/desk/img/scanner/honeywell03.png'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            + "<img src='/static/c6sh/desk/img/scanner/honeywell04.png'>"
            + "</p>"
            + "<p>"
            + "<img src='/static/c6sh/desk/img/scanner/honeywell05.png'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            + "<img src='/static/c6sh/desk/img/scanner/honeywell06.png'>"
            + "</p>"
            + "<p>"
            + "<img src='/static/c6sh/desk/img/scanner/honeywell07.png'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            + "<img src='/static/c6sh/desk/img/scanner/honeywell08.png'>"
            + "</p>");
    },

    process: function (command) {
        if (command.slice(0, 1) !== "/") {
            command = "/" + command;
        }
        if (typeof commands[command] !== 'undefined') {
            commands[command]();
            return true;

        } else if (command.slice(0, 5) === '/ping') {
            commands['/ping'](command);
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
