var preorder = {
    /*
     The preorder object delals with everything directly related to redeeming a preorder ticket
     */

    redeem: function (secret) {
        loading.start();
        $.ajax({
            url: '/api/preorderpositions/?secret=' + secret,
            method: 'GET',
            dataType: 'json',
            success: function (data, status, jqXHR) {
                loading.end();
                $("#preorder-input").typeahead('val', "");
                
                if (data.count !== 1) {
                    if (data.count > 1) {
                        dialog.show_error('Secret is not unique.');
                        return;
                    } else {
                        dialog.show_error('Unknown secret.');
                        return;
                    }
                }
                var res = data.results[0];
                if (res.is_redeemed) {
                    dialog.show_error('Ticket already redeemed.');
                    return;
                } else if (!res.is_paid) {
                    dialog.show_error('Ticket has not been paid for.');
                    return;
                }

                transaction.add_preorder(secret, res.product_name + ' - ' + secret.substring(0, 5) + '...');
		preorder.take_focus();
            },
            headers: {
                'Content-Type': 'application/json'
            },
            error: function (jqXHR, status, error) {
                console.log(jqXHR.statusText);
                dialog.show_error(jqXHR.statusText);
                loading.end();
            }
        });
    },
    
    take_focus: function () {
        window.setTimeout(function () {
            // This is a bit of a hack but it works very well to fix cases
            // where a simple .focus() call won't work because it another event
            // takes focus that is called slightly *after* this event.
            $("#preorder-input").focus().typeahead('val', "");
        }, 100);
    },

    init: function () {
        // Initializations at page load time
        $("#preorder-input").keyup(function (e) {
            if (e.keyCode == 13) { // Enter
                var secret = $.trim($("#preorder-input").val());
                if (secret === "") {
                    return;
                }
                preorder.redeem(secret);
                $("#preorder-input").typeahead("val", "").blur();
            }
        });
        
        $('body').mouseup(function (e) {
            // Global catch-all "if the finger goes up, we reset the focus"
            if (!$('body').hasClass('has-modal') && !$(e.target).is("input, #btn-checkout")) {
                $("#preorder-input").focus().typeahead("close");
            }
        });
        
        preorder.take_focus();

        $('#preorder-input').typeahead(null, {
            name: 'preorder-tickets',
            display: 'value',
            minLength: 6,
            source: preorder._typeahead_source
        });
    },

    _typeahead_source: new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 4,
        remote: {
            url: '/api/preorderpositions/?search=%QUERY',
            wildcard: '%QUERY',
            transform: function (object) {
                var results = object.results;
                var secrets = [];
                var reslen = results.length;
                for (var i = 0; i < reslen; i++) {
                    secrets.push({
                        value: results[i].secret,
                        count: 1
                    });
                }
                return secrets;
            }
        }
    })
};
