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
        });
    }
};