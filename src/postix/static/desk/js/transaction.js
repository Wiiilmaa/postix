var transaction = {
    /*
     The transaction object deals with creating a cart and executing a transaction.
     */

    positions: [],  // Positions in the current cart
    post_sale: false,  // true if we have just completed a sale
    last_id: null,
    _touch_scrolling: false,
    _touch_scroll_start_mpos: 0,
    _touch_scroll_start_cpos: 0,

    add_preorder: function (secret, product_name, pack_list) {
        for (var i = 0; i < transaction.positions.length; i++) {
            var pos = transaction.positions[i];
            if (pos.type == 'redeem') {
                if (pos.secret == secret) {
                    dialog.show_error(gettext('This preorder alread is in your cart.'));
                    return;
                }
            }
        }
        transaction._add_position({
            'secret': secret,
            'price': '0.00',
            'type': 'redeem'
        }, product_name, '0.00', pack_list)
    },

    add_product: function (prod_id) {
        // Adds the product with the ID prod_id to the cart
        var product = productlist.products[prod_id];

        transaction._add_position({
            'product': product.id,
            'price': product.price,
            'type': 'sell'
        }, product.name, product.price, product.pack_list)
    },

    upgrade: function (pos_id, bypass_price) {
        var pos = transaction.positions[pos_id];
        var new_price = (parseFloat(pos.price) + parseFloat(bypass_price)).toFixed(2),
            new_bypass_price;

        if (typeof pos.bypass_price !== 'undefined') {
            new_bypass_price = (parseFloat(pos.bypass_price) + parseFloat(bypass_price)).toFixed(2);
        } else {
            new_bypass_price = parseFloat(bypass_price).toFixed(2);
        }

        pos.bypass_price = new_bypass_price;
        pos.price = new_price;
        $($("#cart .cart-line").get(pos_id)).find(".cart-price").text(new_price);
        transaction._render();
    },

    _add_position: function (obj, name, price, info) {
        if (transaction.post_sale) {
            transaction.clear();
        }

        obj._title = name;
        transaction.positions.push(obj);

        var productname = $("<span>").addClass("cart-product").text(name);
        if (info) {
            productname.append($("<small>").append("<br/>").append(info));
        }

        $("<div>").addClass("cart-line").append(
            productname
        ).append(
            $("<span>").addClass("cart-price").text(price)
        ).append(
            $("<span>").addClass("cart-delete").html(
                "<button class='btn-delete btn btn-sm btn-danger'>"
                + "<span class='glyphicon glyphicon-remove'></span>"
                + "</button>"
            )
        ).appendTo($("#cart-inner"));

        transaction._render();
        transaction._scroll(-9000000);
    },

    perform: function () {
        // This tries to the transaction. If additional input is required,the
        // dialog object is used to present a dialog and then calls this again,
        if (transaction.positions.length === 0) {
            dialog.show_error(gettext('Cart is empty.'));
            return;
        }

        loading.start();
        $.ajax({
            url: '/api/transactions/',
            method: 'POST',
            dataType: 'json',
            data: JSON.stringify({
                positions: transaction.positions
            }),
            success: function (data, status, jqXHR) {
                loading.end();
                $('#lower-right').addClass('post-sale').find('.panel-heading span').text(gettext('Last transaction'));

                var i, total = 0;
                for (i = 0; i < transaction.positions.length; i++) {
                    total += parseFloat(transaction.positions[i].price);
                }
                if (total > 0.001) {
                    $("#post-sale-given input").focus();
                }

                transaction._scroll(0);
                transaction.post_sale = true;
                transaction.last_id = data.id;
                dialog.flash_success(gettext('Transaction complete'));
                signalNext();
            },
            headers: {
                'Content-Type': 'application/json'
            },
            error: function (jqXHR, status, error) {
                loading.end();
                if (jqXHR.status == 400) {
                    var data = JSON.parse(jqXHR.responseText);
                    var i = 0, pos;
                    for (i = 0; i < data.positions.length; i++) {
                        pos = data.positions[i];
                        if (!pos.success) {
                            if (pos.type == 'confirmation') {
                                dialog.show_confirmation(i, pos.message, pos.missing_field, pos.bypass_price);
                            } else if (pos.type == 'input') {
                                dialog.show_list_input(i, pos.message, pos.missing_field, pos.bypass_price);
                            } else {
                                dialog.show_error(pos.message);
                            }
                            break;
                        }
                    }
                } else {
                    console.log(jqXHR.statusText);
                    dialog.show_error(jqXHR.statusText);
                }
            }
        });
    },

    remove: function (pos_nr) {
        // Remove the cart item at position pos_nr from the cart
        $("#cart .cart-line").get(pos_nr).remove();
        transaction.positions.remove(pos_nr);
        transaction._render();
    },

    reverse_last: function () {
        dialog.show_confirmation(null, gettext('Do you really want to reverse the last transaction?'),
            transaction._do_reverse_last)
    },

    _do_reverse_last: function () {
        if (!transaction.last_id) {
            dialog.show_error(gettext("The last transaction is not known."));
        }

        loading.start();
        $.ajax({
            url: '/api/transactions/' + transaction.last_id + '/reverse/',
            method: 'POST',
            dataType: 'json',
            data: '',
            success: function (data, status, jqXHR) {
                transaction.last_id = data.id;
                loading.end();
                $("#lower-right").addClass("reversed");
                dialog.flash_success(gettext('The transaction has been reversed.'));
            },
            headers: {
                'Content-Type': 'application/json'
            },
            error: function (jqXHR, status, error) {
                loading.end();
                if (jqXHR.status == 400) {
                    var data = JSON.parse(jqXHR.responseText);
                    dialog.show_error(data.message);
                } else {
                    console.log(jqXHR.statusText);
                    dialog.show_error(jqXHR.statusText);
                }
            }
        });
    },

    clear: function () {
        // Remove all positions from the cart
        transaction.positions = [];
        $("#cart-inner").html("");
        transaction._render();
        transaction.post_sale = false;
        transaction.last_id = null;
        $('#lower-right').removeClass('post-sale reversed').find('.panel-heading span').text(
            gettext('Current transaction'));
    },

    _render: function () {
        // Calculate and display the current cart total
        var i, total = 0;
        for (i = 0; i < transaction.positions.length; i++) {
            total += parseFloat(transaction.positions[i].price);
        }
        $("#checkout-total span").text(total.toFixed(2));
        $("#post-sale-total span").text(total.toFixed(2));
        $("#post-sale-given input").val("");
        $("#post-sale-change span").text("0.00");
        transaction._scroll();
    },

    _calculate_change: function (e) {
        if (e.which && (e.which === 13 || e.which == 9)) {
            $("#preorder-input").focus();
            e.preventDefault();
            return;
        }
        if ($("#post-sale-given input").val().match(/.*[a-zA-Z].*/)) {
            // This is probably a preorder secret, lets enter it there.
            $("#preorder-input").val($("#post-sale-given input").val()).focus();
            $("#post-sale-given input").val("");
            return;
        }

        var total = parseFloat($.trim($("#post-sale-total span").text())), given;
        if (!$("#post-sale-given input").val()) {
            given = 0;
        } else {
            given = parseFloat($.trim($("#post-sale-given input").val().replace(/,/, ".")));
        }
        var change = given - total;
        $("#post-sale-change span").text(change.toFixed(2));
    },

    _scroll: function (position) {
        var cart = $("#cart"),
            inner = $("#cart-inner");

        if (position === undefined) {
            position = parseInt(inner.css('top'));
        }

        var minpos = Math.min(cart.height()-inner.height(), 0);
        position = Math.max(minpos, Math.min(0, position));

        cart.find('.upfade').css('height', Math.min(-position*2, 40));
        cart.find('.downfade').css('height', Math.min((position-minpos)*2, 40));
        inner.css('top', position);
    },

    _touch_scroll_start: function (e) {
        if (e.button === 0) {
            transaction._touch_scrolling = true;
            transaction._touch_scroll_start_cpos = parseInt($('#cart-inner').css('top'));
            transaction._touch_scroll_start_mpos = e.clientY;
        }
    },

    _touch_scroll_move: function (e) {
        if (transaction._touch_scrolling) {
            transaction._scroll(transaction._touch_scroll_start_cpos+(e.clientY-transaction._touch_scroll_start_mpos));
        }
    },

    _touch_scroll_end: function (e) {
        if (e.button === 0) {
            transaction._touch_scrolling = false;
        }
    },

    init: function () {
        // Initializations at page load time
        $("#btn-clear").mousedown(transaction.clear);
        $("#btn-checkout").mousedown(transaction.perform);
        $("#btn-reverse").mousedown(transaction.reverse_last);
        $("#cart-inner").html("").on("mousedown", ".cart-delete button", function () {
            var $row = $(this).parent().parent();
            transaction.remove($row.index());
        });
        $("#post-sale-given input")
            .keydown(transaction._calculate_change)
            .keyup(transaction._calculate_change)
            .change(transaction._calculate_change);
        transaction._render();

        $('#cart').mousedown(transaction._touch_scroll_start);
        $('body').mousemove(transaction._touch_scroll_move).mouseup(transaction._touch_scroll_end);
        $(window).resize(function () {
            transaction._scroll();
        });
    }
};
