var keyboard = {

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