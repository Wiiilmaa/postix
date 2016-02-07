import decimal

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = "Core"

    def ready(self):
        from . import admin


DECIMAL_CONTEXT = decimal.Context(prec=10, rounding=decimal.ROUND_HALF_UP)
DECIMAL_QUANTIZE = decimal.Decimal('0.01')