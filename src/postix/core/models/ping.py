from tempfile import TemporaryFile

import qrcode
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from .cashdesk import Cashdesk

MAX_LENGTH = 20


def generate_ping(cashdesk: Cashdesk) -> None:
    ping = Ping.objects.create()
    cashdesk.printer.print_image(ping.get_qr_code())


def generate_ping_secret():
    prefix = '/ping '
    return prefix + get_random_string(length=MAX_LENGTH - len(prefix))


class Ping(models.Model):
    pinged = models.DateTimeField(auto_now_add=True)
    ponged = models.DateTimeField(null=True, blank=True)
    secret = models.CharField(max_length=MAX_LENGTH, default=generate_ping_secret)
    synced = models.BooleanField(default=False)

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

    def pong(self):
        if not self.ponged:
            self.ponged = now()
            self.save()
