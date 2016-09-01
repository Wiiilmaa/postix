import logging
import subprocess
import time
from collections import defaultdict
from string import ascii_uppercase

from c6sh.core.models.settings import EventSettings


SEPARATOR = '\u2500' * 42 + '\r\n'


class CashdeskPrinter:
    def __init__(self, printer):
        self.printer = printer

    @staticmethod
    def _format_number(number):
        formatted_value = '{:.2f}'.format(float(number))
        gap = ' ' * (7 - len(formatted_value))
        return gap + formatted_value

    def send(self, data):
        lpr = subprocess.Popen(['/usr/bin/lpr', '-l', '-P', self.printer], stdin=subprocess.PIPE)
        if isinstance(data, str):
            data = data.encode('cp437')
        lpr.stdin.write(data)
        lpr.stdin.close()
        time.sleep(0.1)

    def open_drawer(self):
        self.send(bytearray([0x1B, ord('p'), 48, 255, 255]))

    def cut_tape(self):
        self.send(bytearray([0x1D, 0x56, 66, 100]))

    def _build_receipt(self, transaction):
        settings = EventSettings.objects.get()
        total_sum = 0
        position_lines = list()
        tax_sums = defaultdict(int)
        tax_symbols = dict()

        positions = [
            position for position in transaction.positions.all()
            if not position.type == 'redeem'
        ]
        is_cancellation = any(position.type == 'reverse' for position in positions)

        if not positions:
            return

        for position in transaction.positions.all():
            if position.value == 0:
                continue
            total_sum += position.value
            tax_sums[position.tax_rate] += position.tax_value
            if position.tax_rate not in tax_symbols:
                tax_symbols[position.tax_rate] = ascii_uppercase[len(tax_sums) - 1]
            pos_str = ' {product_name} ({tax_str}){gap} {price}'.format(
                product_name=position.product.name,
                tax_str=tax_symbols[position.tax_rate],
                gap=' ' * (29 - len(position.product.name)),
                price=self._format_number(position.value),
            )
            position_lines.append(pos_str)
        total_taxes = sum(tax_sums.values())

        if not position_lines:
            return

        receipt = bytearray([0x1B, 0x61, 1]).decode()  # center text
        receipt += bytearray([0x1B, 0x45, 1]).decode()  # emphasize
        receipt += settings.name + '\r\n\r\n'
        receipt += bytearray([0x1B, 0x45, 0]).decode()  # de-emphasize
        receipt += settings.receipt_address + '\r\n\r\n'

        if is_cancellation:
            receipt += bytearray([0x1B, 0x45, 1]).decode()  # emphasize
            receipt += 'Storno-Rechnung' + '\r\n\r\n'
            receipt += bytearray([0x1B, 0x45, 0]).decode()  # de-emphasize

        receipt += SEPARATOR
        receipt += " Ticket                                EUR\r\n"
        receipt += SEPARATOR

        receipt += '\r\n'.join(position_lines)
        receipt += '\r\n'
        receipt += SEPARATOR
        receipt += bytearray([0x1B, 0x61, 2]).decode()  # right-align text (0 would be left-align)
        receipt += "Nettosumme:  {}\r\n".format(self._format_number(total_sum - total_taxes))

        for tax in sorted(list(tax_symbols))[::-1]:
            receipt += "MwSt {tax_rate}% ({tax_identifier}):  {tax_amount}\r\n".format(
                tax_rate=tax,
                tax_identifier=tax_symbols[tax],
                tax_amount=self._format_number(tax_sums[tax]),
            )

        receipt += "Summe:  {}\r\n\r\n\r\n".format(self._format_number(total_sum))
        receipt += bytearray([0x1B, 0x61, 1]).decode()  # center text
        receipt += settings.receipt_footer + '\r\n'
        receipt += '{} {}\r\n'.format(
            transaction.datetime.strftime("%d.%m.%Y %H:%M"),
            transaction.session.cashdesk.name,
        )
        receipt += 'Belegnummer: {}\r\n'.format(transaction.pk)
        receipt += '\r\n\r\n'
        return receipt

    def print_receipt(self, transaction, do_open_drawer=True):
        if do_open_drawer:
            self.open_drawer()
        receipt = self._build_receipt(transaction)

        if receipt:
            try:
                # self.send(image_tools.get_imagedata(settings.STATIC_ROOT + '/' + settings.EVENT_RECIPE_HEADER))
                self.send(receipt)
                self.cut_tape()
            except:
                logging.getLogger('django').exception('Printing at {} failed'.format(self.printer))


class DummyPrinter:
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('django')

    def send(self, data):
        self.logger.info('[DummyPrinter] Received data: {}'.format(data))

    def open_drawer(self):
        self.logger.info('[DummyPrinter] Opened drawer')

    def cut_tape(self):
        self.logger.info('[DummyPrinter] Cut tape')

    def print_receipt(self, transaction, do_open_drawer=True):
        receipt = CashdeskPrinter('')._build_receipt(transaction)
        self.logger.info('[DummyPrinter] Printed receipt:\n{}'.format(receipt))
