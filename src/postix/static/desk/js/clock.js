var clock = {
    _tick: function () {
        $.ajax({
            url: '/api/cashdesk/current-time/',
            method: 'GET',
            dataType: 'json',
            data: '',
            success: function (data, status, xhr) {
                $("#clock").text(data.string);
            }
        });
    },

    init: function () {
        window.setInterval(clock._tick, 10000);
        clock._tick();
    }
};
