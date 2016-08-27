var loading = {
    _current_count: 0,

    start: function () {
        loading._current_count++;
        $("#loading").toggle(loading._current_count > 0);
    },

    end: function () {
        loading._current_count--;
        $("#loading").toggle(loading._current_count > 0);
    }
};