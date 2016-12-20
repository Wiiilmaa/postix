from tempfile import TemporaryFile

import qrcode
from django.db import models
from django.utils.crypto import get_random_string

from .cashdesk import Cashdesk


def generate_ping(cashdesk: Cashdesk) -> None:
    ping = Ping.objects.create()
    cashdesk.printer.print_image(ping.get_qr_code())


def generate_ping_secret():
    return '/ping ' + get_random_string(length=15)


class Ping(models.Model):
    pinged = models.DateTimeField(auto_now_add=True)
    ponged = models.DateTimeField(null=True, blank=True)
    secret = models.CharField(max_length=20, default=generate_ping_secret)

    def get_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )
        qr.add_data(self.secret)
        qr.make()
        f = TemporaryFile()
        img = qr.make_image()
        img.save(f)
        return f
