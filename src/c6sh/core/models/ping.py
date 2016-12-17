from django.db import models
from django.utils.crypto import get_random_string


def generate_ping_secret():
    return '#ping' + get_random_string(length=15)


class Ping(models.Model):
    pinged = models.DateTimeField(auto_now_add=True)
    ponged = models.DateTimeField(null=True, blank=True)
    secret = models.CharField(max_length=20, default=generate_ping_secret)
