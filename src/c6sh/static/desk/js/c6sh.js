/*global Bloodhound, $*/

// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
    var rest = this.slice((to || from) + 1 || this.length);
    this.length = from < 0 ? this.length + from : from;
    return this.push.apply(this, rest);
};

var productlist = {
    products: {},
    _load_list: function (url) {
        $.getJSON(url, function(data) {
            var i, product;
            for (i = 0; i < data.results.length; i++) {
                product = data.results[i];
                if (product.is_available) {
                    productlist.products[product.id] = product;
                    $("<div>").addClass("product").append(
                        $("<button>").addClass("btn btn-default btn-block").attr("data-id", product.id).append(
                            $("<strong>").text(product.name)
                        ).append($("<br>")).append(product.price + ' €')
                    ).appendTo($("#product-view"));
                }
            }
            if (data.next !== null) {
                productlist._load_list(data.next);
            }
        });
    },
    load_all: function() {
        $("#product-view").html("");
        productlist.products = {};
        productlist._load_list('/api/products/');
    },
    init: function () {
        productlist.load_all();
    }
};

var preorder = {
    current_preorder: {},
    _perform: function () {
        
    },
    redeem: function (secret) {
        preorder.current_preorder.secret = secret;
        preorder._perform();
    },
    init: function () {
        
    }
};

var transaction = {
    positions: [],
    add_product: function (prod_id) {
        var product = productlist.products[prod_id];
        
        transaction.positions.push({
            'product': product.id,
            'price': product.price,
            'type': 'sell'
        });
        
        $("<div>").addClass("cart-line").append(
            $("<span>").addClass("cart-product").text(product.name)
        ).append(
            $("<span>").addClass("cart-price").text(product.price)
        ).append(
            $("<span>").addClass("cart-delete").html(
                "<button class='btn-delete btn btn-sm btn-danger'>"
                + "<span class='glyphicon glyphicon-remove'></span>"
                + "</button>"
            )
        ).appendTo($("#cart"));
        
        transaction._render();
    },
    perform: function () {
        // TODO
    },
    remove: function (pos_nr) {
        $("#cart .cart-line").get(pos_nr).remove();
        transaction.positions.remove(pos_nr);
        transaction._render();
    },
    clear: function () {
        transaction.positions = [];
        $("#cart").html("");
        transaction._render();
    },
    _render: function () {
        var i, total = 0;
        for (i = 0; i < transaction.positions.length; i++) {
            total += parseFloat(transaction.positions[i].price);
        }
        $("#checkout-total span").text(total.toFixed(2));
    },
    init: function () {
        $("#product-view").on("click", ".product button", function () {
            transaction.add_product($(this).attr("data-id"));
        });
        $("#btn-clear").click(transaction.clear);
        $("#btn-checkout").click(transaction.perform);
        $("#cart").html("").on("click", ".cart-delete button", function () {
            var $row = $(this).parent().parent();
            transaction.remove($row.index());
        });
        transaction._render();
    }
};

var confirm_dialog = {
    show_list_input: function (pos_id, message, listid, field_name) {
        // TODO
    },
    show_error: function (message) {
        // TODO
    },
    show_confirmation: function (pos_id, message, field_name) {
        // TODO
    },
    init: function () {
        
    }
};


$(function () {
    productlist.init();
    confirm_dialog.init();
    transaction.init();
    preorder.init();
    /*
    $('#btn-checkout').mousedown(function() {
        $('#lower-right').addClass('post-sale');
    });
    $('#btn-clear').mousedown(function() {
        $('#lower-right').removeClass('post-sale');
    });
    $('.product button').mousedown(function() {
        $('body').addClass('has-modal');
    });
    $('#btn-cancel').mousedown(function() {
        $('body').removeClass('has-modal');
    });
    var preSaleTickets = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 4,
      remote: {
        url: '/api/preorderpositions/?search=%QUERY',
        wildcard: '%QUERY',
        transform: function(object) {
            results = object.results;
            secrets = [];
            for(var preorder in results){
                secrets.push(
                    {
                        value: results[preorder].secret,
                        count: 1
                    });
            }
            return secrets;
        }
      }
    });

    $('#preorder-input').typeahead(null, {
      name: 'preSaleTickets',
      display: 'value',
      minLength: 5,
      source: preSaleTickets
    });
    */
});