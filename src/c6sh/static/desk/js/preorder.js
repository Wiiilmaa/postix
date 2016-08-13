var preorder = {
    /*
     The preorder object delals with everything directly related to redeeming a preorder ticket
     */

    redeem: function (secret) {
        // TODO: Block interface while loading
        $.ajax({
            url: '/api/preorderpositions/?secret=' + secret,
            method: 'GET',
            dataType: 'json',
            success: function (data, status, jqXHR) {
                // TODO: Render successful message
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

                transaction.add_preorder(secret, res.product_name + ' - ' + secret.substring(0, 5) + '...')
            },
            headers: {
                'Content-Type': 'application/json'
            },
            error: function (jqXHR, status, error) {
                console.log(jqXHR.statusText);
                dialog.show_error(jqXHR.statusText);
            }
        });
    },

    init: function () {
        // Initializations at page load time
        $("#preorder-input").keyup(function (e) {
            if (e.keyCode == 13) { // Enter
                preorder.redeem($.trim($("#preorder-input").val()));
                $("#preorder-input").val("").blur();
            }
        });

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
                for (var preorder in results) {
                    secrets.push(
                        {
                            value: results[preorder].secret,
                            count: 1
                        });
                }
                return secrets;
            }
        }
    })
};
