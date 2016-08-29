var dialog = {
    /*
     The dialog object deals with all questions asked to the cashier
     */

    // Temporary information for the dialog currently shown
    _handler: null,
    _pos_id: null,
    _type: null,
    _list_id: null,

    show_list_input: function (pos_id, message, handler) {
        // Shows a dialog that is related to cart position pos_id and asks
        // the user to input a text into a field with name handler and the message message.
        // If the dialog is confirmed, the current transaction is re-tried.
        // If handler is of the form list_\d+ it will be assumed that the latter part
        // is the ID of a ListConstraint that can be used for autocompletion.
        // If handler is a function, it will be called on dialog confirmation instead of
        // the default behavior.
        dialog._pos_id = pos_id;
        dialog._handler = handler;
        dialog._type = 'input';
        if (typeof handler === "string" && handler.match(/list_\d+/)) {
            dialog._list_id = parseInt(handler.substring(5));
        } else {
            dialog._list_id = null;
        }

        $("#modal-title").text(pos_id !== null ? transaction.positions[pos_id]._title : 'Input required');
        $("#modal-text").text(message);
        $("#modal-input-wrapper").show();
        $("#btn-continue").show();
        $("#btn-cancel").show();
        $("#btn-dismiss").hide();
        $("body").addClass("has-modal");
        $("#modal .panel").removeClass("panel-success").addClass("panel-danger");
    },

    show_error: function (message, pos_id) {
        // Shows an error message, optionally related to the cart position pos_id.
        dialog._type = 'error';

        if (typeof pos_id === "undefined") {
            pos_id = null;
        }
        
        $("#modal-title").text(pos_id !== null ? transaction.positions[pos_id]._title : 'Error');
        $("#modal-text").text(message);
        $("#modal-input-wrapper").hide();
        $("#btn-continue").hide();
        $("#btn-cancel").show();
        $("#btn-dismiss").hide();
        $("body").addClass("has-modal");
        $("#modal .panel").removeClass("panel-success").addClass("panel-danger");
    },

    show_success: function (message) {
        // Shows a success message
        dialog._type = 'success';
        dialog._pos_id = null;

        $("#modal-title").text("Success");
        $("#modal-text").text(message);
        $("#modal-input-wrapper").hide();
        $("#btn-continue").hide();
        $("#btn-cancel").hide();
        $("#btn-dismiss").show();
        $("body").addClass("has-modal");
        $("#modal .panel").addClass("panel-success").removeClass("panel-danger");
    },

    show_confirmation: function (pos_id, message, handler) {
        // Shows a dialog related to the cart entry pos_id and the message message,
        // asking the user to confirm something. If he/she does, the of the name
        // handler will be set to true in the transaction and the transaction will be
        // re-tried. If handler is a function, it will be called if the user selects the
        // positive option instead of the default behaviour.
        dialog._type = 'confirmation';
        dialog._pos_id = pos_id;
        dialog._handler = handler;
        $("#modal-title").text(pos_id !== null ? transaction.positions[pos_id]._title : 'Confirmation required');
        $("#modal-text").text(message);
        $("#modal-input-wrapper").hide();
        $("#btn-continue").show();
        $("#btn-dismiss").hide();
        $("#btn-cancel").show();
        $("body").addClass("has-modal");
        $("#modal .panel").removeClass("panel-success").addClass("panel-danger");
    },

    _continue: function () {
        // Called if the user confirms the dialog.
        var val;
        if (dialog._type === 'confirmation') {
            val = true;
        } else if (dialog._type === 'input') {
            val = $("#modal-input").val();
        }
        if (typeof dialog._handler === "function") {
            dialog._handler(val);
        } else if (dialog._pos_id !== null) {
            transaction.positions[dialog._pos_id][dialog._handler] = val;
            transaction.perform();
        }
        dialog.reset();
    },

    reset: function () {
        // Resets the internal object state
        $('body').removeClass('has-modal');
        dialog._pos_id = null;
        dialog._handler = null;
        dialog._type = null;
    },

    keypress: function (e) {
        if (e.keyCode === 27) {
            // Close dialog when ESC was pressed
            dialog.reset();
            e.preventDefault();
            e.stopPropagation();
            return false;
        } else if (e.keyCode === 13) {
            if ($("#btn-continue").is(':visible')) {
                // Confirm dialog with ENTER
                dialog._continue();
            } else {
                // Confirming not available, closing then
                dialog.reset();
            }
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    },
    
    init: function () {
        // Initializations at page load time
        $('#btn-cancel').mousedown(dialog.reset);
        $('#btn-dismiss').mousedown(dialog.reset);
        $("#btn-continue").mousedown(dialog._continue);

        $('#modal-input').typeahead(null, {
            name: 'dialog-input',
            display: function (obj) {
                return obj.identifier;
            },
            templates: {
                suggestion: function (obj) {
                    return '<div>' + obj.identifier + ' (' + obj.name + ')</div>';
                }
            },
            minLength: 3,
            source: dialog._typeahead_source
        });
    },

    _typeahead_source: new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 4,
        remote: {
            url: '/api/listconstraintentries/?listid=%LISTID&search=%QUERY',
            prepare: function (query, settings) {
                settings.url = settings.url.replace('%QUERY', encodeURIComponent(query));
                settings.url = settings.url.replace('%LISTID', encodeURIComponent(dialog._list_id));
                return settings;
            },
            transform: function (object) {
                if (object.count < 1) {
                    return [];
                }
                var results = object.results;
                var suggs = [];
                var reslen = results.length;
                for (var i = 0; i < reslen; i++) {
                    suggs.push(results[i]);
                }
                return suggs;
            }
        }
    })

};
