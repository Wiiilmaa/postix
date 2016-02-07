import decimal


DECIMAL_CONTEXT = decimal.Context(prec=10, rounding=decimal.ROUND_HALF_UP)
DECIMAL_QUANTIZE = decimal.Decimal('0.01')


def round_decimal(d):
    return decimal.Decimal(d).quantize(DECIMAL_QUANTIZE, DECIMAL_CONTEXT)