/*global Bloodhound, $*/
var productlist = {
    _load_list: function (url) {
        $.getJSON(url, function(data) {
            var i, product;
            for (i = 0; i < data.results.length; i++) {
                product = data.results[i];
                if (product.is_available) {
                    $("<div>").addClass("product").append(
                        $("<button>").addClass("btn btn-default btn-block").append(
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
        productlist._load_list('/api/products/');
    },
    init: function () {
        $("#product-view").html("");
        productlist.load_all();
    }
};

var transaction = {
    add_product: function () {

    },
    perform: function () {

    },
    remove: function () {

    },
    clear: function () {

    },
    init: function () {

    }
};

var confirm_dialog = {
    show_list_input: function (message, listid, field_name) {

    },
    show_confirmation: function (message, field_name) {

    }
};


$(function () {
    productlist.init();
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