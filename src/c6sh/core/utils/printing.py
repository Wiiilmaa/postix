import logging
import subprocess
import time
from collections import defaultdict
from decimal import Decimal
from string import ascii_uppercase
from typing import Union

from django.utils.translation import ugettext as _

from c6sh.core.models import Transaction

SEPARATOR = '\u2500' * 42 + '\r\n'


class CashdeskPrinter:
    def __init__(self, printer: str) -> None:
        self.printer = printer

    @staticmethod
    def _format_number(number: Decimal) -> str:
        formatted_value = '{:.2f}'.format(float(number))
        gap = ' ' * (7 - len(formatted_value))
        return gap + formatted_value

    def send(self, data: Union[str, bytes]) -> None:
        lpr = subprocess.Popen(['/usr/bin/lpr', '-l', '-P', self.printer], stdin=subprocess.PIPE)
        if isinstance(data, str):
            data = data.encode('cp437')
        lpr.stdin.write(data)
        lpr.stdin.close()
        time.sleep(0.1)

    def open_drawer(self) -> None:
        self.send(bytearray([0x1B, ord('p'), 48, 255, 255]))

    def cut_tape(self) -> None:
        self.send(bytearray([0x1D, 0x56, 66, 100]))

    def _build_receipt(self, transaction: Transaction) -> Union[None, str]:
        from c6sh.core.models import EventSettings
        settings = EventSettings.objects.get()
        total_sum = 0
        position_lines = list()
        tax_sums = defaultdict(int)
        tax_symbols = dict()

        positions = [
            position for position in transaction.positions.all()
            if not (position.type == 'redeem' and position.value == Decimal('0.00'))
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

            formatargs = {
                'product_name': position.product.name,
                'tax_str': tax_symbols[position.tax_rate],
                'gap': ' ' * (29 - len(position.product.name)),
                'price': self._format_number(position.value),
                'upgrade': _('Upgrade'),
                'upgradegap': ' ' * (29 - len(_('Upgrade'))),
            }
            if position.has_constraint_bypass:
                position_lines.append(' {product_name}'.format(**formatargs))
                position_lines.append(' {upgrade} ({tax_str}){upgradegap} {price}'.format(**formatargs))
            else:
                pos_str = ' {product_name} ({tax_str}){gap} {price}'.format(**formatargs)
                position_lines.append(pos_str)
        total_taxes = sum(tax_sums.values())

        if not position_lines:
            return

        # Only get a new receipt ID after all early outs have passed
        # to make sure that we'll end up with actual consecutive numbers
        if not transaction.receipt_id:
            transaction.set_receipt_id(retry=3)
            is_copy = False
        else:
            is_copy = True

        receipt = bytearray([0x1B, 0x61, 1]).decode()  # center text
        receipt += bytearray([0x1B, 0x45, 1]).decode()  # emphasize
        receipt += settings.name + '\r\n\r\n'
        receipt += bytearray([0x1B, 0x45, 0]).decode()  # de-emphasize
        receipt += settings.receipt_address + '\r\n\r\n'

        if is_cancellation:
            receipt += bytearray([0x1B, 0x45, 1]).decode()  # emphasize
            receipt += _('Cancellation') + '\r\n\r\n'
            receipt += bytearray([0x1B, 0x45, 0]).decode()  # de-emphasize

        if is_copy:
            receipt += bytearray([0x1B, 0x45, 1]).decode()  # emphasize
            receipt += _('Receipt copy') + '\r\n\r\n'
            receipt += bytearray([0x1B, 0x45, 0]).decode()  # de-emphasize

        receipt += SEPARATOR
        receipt += " {: <26}            EUR\r\n".format(_('Ticket'))
        receipt += SEPARATOR

        receipt += '\r\n'.join(position_lines)
        receipt += '\r\n'
        receipt += SEPARATOR
        receipt += bytearray([0x1B, 0x61, 2]).decode()  # right-align text (0 would be left-align)
        receipt += _("Net sum:  {}").format(self._format_number(total_sum - total_taxes))
        receipt += '\r\n'

        for tax in sorted(list(tax_symbols))[::-1]:
            receipt += _("Tax {tax_rate}% ({tax_identifier}):  {tax_amount})").format(
                tax_rate=tax,
                tax_identifier=tax_symbols[tax],
                tax_amount=self._format_number(tax_sums[tax]),
            )
            receipt += '\r\n'

        receipt += _("Total:  {}").format(self._format_number(total_sum))
        receipt += '\r\n' * 3
        receipt += bytearray([0x1B, 0x61, 1]).decode()  # center text
        receipt += settings.receipt_footer + '\r\n'
        receipt += '{} {}\r\n'.format(
            transaction.datetime.strftime("%d.%m.%Y %H:%M"),
            transaction.session.cashdesk.name,
        )
        receipt += _('Receipt number: {}').format(transaction.receipt_id)
        receipt += '\r\n\r\n\r\n'
        return receipt

    def print_receipt(self, transaction: Transaction, do_open_drawer: bool=True) -> None:
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
    def __init__(self, *args, **kwargs) -> None:
        self.logger = logging.getLogger('django')

    def send(self, data) -> None:
        self.logger.info('[DummyPrinter] Received data: {}'.format(data))

    def open_drawer(self) -> None:
        self.logger.info('[DummyPrinter] Opened drawer')

    def cut_tape(self) -> None:
        self.logger.info('[DummyPrinter] Cut tape')

    def print_receipt(self, transaction: Transaction, do_open_drawer: bool=True) -> None:
        receipt = CashdeskPrinter('')._build_receipt(transaction)
        if receipt is not None:
            self.logger.info('[DummyPrinter] Printed receipt:\n{}'.format(receipt))
