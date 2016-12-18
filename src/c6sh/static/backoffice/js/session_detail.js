$(function() {
    new QRCode(document.getElementById("qrcode"), {
        'width': 128,
        'height': 128,
        'text': $("#qrcodedata").html()
    });
});
