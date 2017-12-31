$(function() {
    new QRCode(document.getElementById("qrcode"), {
        'width': 256,
        'height': 256,
        'text': $("#qrcodedata").html()
    });
});
