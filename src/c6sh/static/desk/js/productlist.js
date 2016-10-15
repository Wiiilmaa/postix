var productlist = {
    /*
     The productlist object deals with loading and rendering the big list of products
     */

    products: {},  // A list of products known to the frontend
    _touch_scrolling: false,
    _touch_scroll_start_mpos: 0,
    _touch_scroll_start_cpos: 0,
    _touch_scroll_abs_diff: 0,
    _touch_product: true,

    _load_list: function (url) {
        // Loads the list of products from a given API URL and append the products to the list.
        // This calls itself recursively to deal with pagination in the API
        $.getJSON(url, function(data) {
            var i, product;
            for (i = 0; i < data.results.length; i++) {
                product = data.results[i];
                if (product.is_available) {
                    productlist.products[product.id] = product;
                    var btn = $("<button>").addClass("btn btn-default btn-block").attr("data-id", product.id).append(
                            $("<strong>").text(product.name)
                        ).append($("<br>")).append(product.price + ' €');
                    if (product.requires_authorization) {
                        btn.append(" ").append($("<span>").addClass("glyphicon glyphicon-lock"))
                    }
                    $("<div>").addClass("product").append(btn).appendTo($("#product-view-inner"));
                }
            }
            productlist._scroll();
            if (data.next !== null) {
                productlist._load_list(data.next);
            }
        });
    },

    load_all: function() {
        // Clears the current list and re-loads it from the API
        $("#product-view-inner").html("");
        productlist.products = {};
        productlist._load_list('/api/products/');
    },

    _scroll: function (position) {
        var outer = $("#product-view"),
            inner = $("#product-view-inner");

        if (position === undefined) {
            position = parseInt(inner.css('top'));
        }

        var minpos = Math.min(outer.height()-inner.height(), 0);
        position = Math.max(minpos, Math.min(0, position));

        outer.find('.upfade').css('height', Math.min(-position*2, 40));
        outer.find('.downfade').css('height', Math.min((position-minpos)*2, 40));
        inner.css('top', position);
    },

    _touch_scroll_start: function (e) {
        productlist._touch_product = $(e.target).attr("data-id");
        if ($("#product-view-inner").height() >= $("#product-view").height()) {
            // Product list is long enough that we require scrolling at all
            if (e.button === 0) {
                productlist._touch_scrolling = true;
                productlist._touch_scroll_start_cpos = parseInt($("#product-view-inner").css('top'));
                productlist._touch_scroll_start_mpos = e.clientY;
                productlist._touch_scroll_abs_diff = 0;
            }
        }
    },

    _touch_scroll_move: function (e) {
        if (productlist._touch_scrolling) {
            productlist._touch_scroll_abs_diff += Math.abs(e.clientY-productlist._touch_scroll_start_mpos);
            productlist._scroll(productlist._touch_scroll_start_cpos+(e.clientY-productlist._touch_scroll_start_mpos));
        }
    },

    _touch_scroll_end: function (e) {
        if (productlist._touch_scrolling) {
            if ($(e.target).is("button") && productlist._touch_scroll_abs_diff < 10) {
                transaction.add_product(productlist._touch_product);
            }
        } else if (productlist._touch_product) {
            transaction.add_product(productlist._touch_product);
        }
        if (e.button === 0) {
            productlist._touch_scrolling = false;
            productlist._touch_product = null;
        }
    },

    init: function () {
        // Initializations necessary at page load time
        productlist.load_all();

        $('#product-view').mousedown(productlist._touch_scroll_start);
        $('body').mousemove(productlist._touch_scroll_move).mouseup(productlist._touch_scroll_end);
        $(window).resize(function () {
            productlist._scroll();
        });
    }
};
