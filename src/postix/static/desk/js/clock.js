var clock = {
    _tick: function () {
        var d = new Date();
        var hr = d.getHours();
        if (hr < 10) {
            hr = "0" + hr;
        }
        var min = d.getMinutes();
        if (min < 10) {
            min = "0" + min;
        }
        $("#clock").text(hr + ":" + min);
    },

    init: function () {
        window.setInterval(clock._tick, 250);
    }
};
