$(function() {
    $(".secret").click(function () {
        document.getElementById("qrcode").innerText = "";
        new QRCode(document.getElementById("qrcode"), {
            'width': 256,
            'height': 256,
            'text': $(this).attr("data-data")
        });
    });
});
