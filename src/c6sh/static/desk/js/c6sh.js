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
        // TODO: Block interface while loading
        $.ajax({
            url: '/api/transactions/',
            method: 'POST',
            dataType: 'json',
            data: JSON.stringify({
                positions: transaction.positions
            }),
            success: function (data, status, jqXHR) {
                // TODO: Render successful message
                transaction.clear();
            },
            headers: {
                'Content-Type': 'application/json'
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status == 400) {
                    var data = JSON.parse(jqXHR.responseText);
                    var i = 0, pos;
                    for (i = 0; i < data.positions.length; i++) {
                        pos = data.positions[i];
                        if (!pos.success) {
                            if (pos.type == 'confirmation') {
                                dialog.show_confirmation(i, pos.message, pos.missing_field);
                            } else if (pos.type == 'input') {
                                dialog.show_list_input(i, pos.message, pos.missing_field);
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
        })
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
        $("#product-view").on("mousedown", ".product button", function () {
            transaction.add_product($(this).attr("data-id"));
        });
        $("#btn-clear").mousedown(transaction.clear);
        $("#btn-checkout").mousedown(transaction.perform);
        $("#cart").html("").on("mousedown", ".cart-delete button", function () {
            var $row = $(this).parent().parent();
            transaction.remove($row.index());
        });
        transaction._render();
    }
};

var dialog = {
    _field_name: null,
    _pos_id: null,
    _type: null,
    
    show_list_input: function (pos_id, message, listid, field_name) {
        dialog._pos_id = pos_id;
        dialog._field_name = field_name;
        dialog._type = 'input';
        
        var pos = transaction.positions[pos_id];
        var product = productlist.products[pos.product];
        $("#modal-title").text(product.name);
        $("#modal-text").text(message);
        $("#modal-input").show();
        $("#btn-continue").show();
        $("body").addClass("has-modal");
    },
    show_error: function (message, pos_id) {
        dialog._type = 'error';
        
        if (pos_id) {
            var pos = transaction.positions[pos_id];
            var product = productlist.products[pos.product];
            $("#modal-title").text(product.name);
        } else {
            $("#modal-title").text("Error");
        }
        $("#modal-text").text(message);
        $("#modal-input").hide();
        $("#btn-continue").hide();
        $("body").addClass("has-modal");
    },
    show_confirmation: function (pos_id, message, field_name) {
        dialog._type = 'confirmation';
        dialog._pos_id = pos_id;
        dialog._field_name = field_name;
        var pos = transaction.positions[pos_id];
        var product = productlist.products[pos.product];
        $("#modal-title").text(product.name);
        $("#modal-text").text(message);
        $("#modal-input").hide();
        $("#btn-continue").show();
        $("body").addClass("has-modal");
    },
    _continue: function () {
        if (dialog._type === 'confirmation') {
            transaction.positions[dialog._pos_id][dialog._field_name] = true;
            transaction.perform();
            dialog.reset();
        } else if (dialog._type === 'input') {
            transaction.positions[dialog._pos_id][dialog._field_name] = $("#modal-input").val();
            transaction.perform();
            dialog.reset();
        }
    },
    reset: function () {
        $('body').removeClass('has-modal');
        dialog._pos_id = null;
        dialog._field_name = null;
        dialog._type = null;
    },
    init: function () {
        $('#btn-cancel').mousedown(dialog.reset);
        $("#btn-continue").mousedown(dialog._continue);
    }
};


$(function () {
    productlist.init();
    dialog.init();
    transaction.init();
    preorder.init();
    /*
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

// Django CSRF token
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
