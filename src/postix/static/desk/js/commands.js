var commands = {

    _info_view: function (content) {
        $("#info-view .content").html(content);
        $("#info-view").show();
    },

    '/help': function (args) {
        commands._info_view("<p><strong>" + gettext("Supported commands:") + "</strong></p>"
            + "<dl class='dl-horizontal'>"
            + "<dt>/scanner</dt><dd>" + gettext("Show reset codes for the barcode scanner") + "</dd>"
            + "<dt>/ping</dt><dd>" + gettext("Initiate a ping") + "</dd>"
            + "<dt>/ping abcde</dt><dd>" + gettext("Save a response to a ping") + "</dd>"
            + "</dl>");
    },

    '/ping': function(args) {
        if (args && args.length > 1) {
            $.ajax({
                url: '/api/cashdesk/pong/',
                method: 'POST',
                dataType: 'json',
                data: JSON.stringify({
                    'pong': args.join(' ')
                }),
                headers: {
                    'Content-Type': 'application/json'
                },
                success: function (data, status, xhr) {
                    dialog.flash_success(gettext('Pong. Thanks!'));
                }
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
                success: function (data, status, xhr) {
                    dialog.flash_success(gettext('Ping printed!'));
                }
            });
        }
    },

    '/scanner': function (args) {
        commands._info_view("<p><strong>" + gettext("Scan the following, in order:") + "</strong></p>"
            + "<p>"
            + "<img src='/static/postix/desk/img/scanner/honeywell01.png'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            + "<img src='/static/postix/desk/img/scanner/honeywell02.png'>"
            + "</p>"
            + "<p>"
            + "<img src='/static/postix/desk/img/scanner/honeywell03.png'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            + "<img src='/static/postix/desk/img/scanner/honeywell04.png'>"
            + "</p>"
            + "<p>"
            + "<img src='/static/postix/desk/img/scanner/honeywell05.png'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            + "<img src='/static/postix/desk/img/scanner/honeywell06.png'>"
            + "</p>"
            + "<p>"
            + "<img src='/static/postix/desk/img/scanner/honeywell07.png'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            + "<img src='/static/postix/desk/img/scanner/honeywell08.png'>"
            + "</p>");
    },

    process: function (command) {
        if (command.slice(0, 1) !== "/") {
            command = "/" + command;
        }
        var args = command.split(" ");
        command = args[0];
        if (typeof commands[command] !== 'undefined') {
            commands[command](args);
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
