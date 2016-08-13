var productlist = {
    /*
     The productlist object deals with loading and rendering the big list of products
     */

    products: {},  // A list of products known to the frontend

    _load_list: function (url) {
        // Loads the list of products from a given API URL and append the products to the list.
        // This calls itself recursively to deal with pagination in the API
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
        // Clears the current list and re-loads it from the API
        $("#product-view").html("");
        productlist.products = {};
        productlist._load_list('/api/products/');
    },

    init: function () {
        // Initializations necessary at page load time
        productlist.load_all();
    }
};
