var keyboard = {

    _escape: function () {
        transaction.clear();
    },

    _delete: function () {
        transaction.remove(transaction.positions.length - 1);
    },
    
    _enter: function () {
        if (transaction.positions.length > 0 && !transaction.post_sale) {
            transaction.perform();
        }
    },

    init: function () {
        $('body').on('keyup', function (e) {
            var tag = e.target.tagName.toLowerCase(),
                processed = false;

            if ($("body").hasClass('has-modal')) {
                // Delegate to dialog module
                dialog.keypress(e);
                return;
            }

            if (tag == 'input' || tag == 'textarea') {
                return;
            }

            var map = {
                27: keyboard._escape,
                13: keyboard._enter,
                46: keyboard._delete
            };

            if (typeof map[e.which] !== "undefined") {
                map[e.which]();
                processed = true;
            }

            if (processed) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
    }
};