import subprocess
import time
from collections import defaultdict
from string import ascii_uppercase

from c6sh.core.models.settings import EventSettings


SEPARATOR = " -----------------------------------------\r\n"
POSITION_LIST_HEADER = """ Ticket                                EUR
 -----------------------------------------
"""


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
        lpr.stdin.write(data)
        lpr.stdin.close()
        time.sleep(0.1)

    def open_drawer(self):
        self.send(bytearray([0x1B, ord('p'), 48, 255, 255]))

    def cut_tape(self):
        self.send(bytearray([0x1D, 0x56, 66, 100]))

    def print_receipt(self, transaction, do_open_drawer=True):
        settings = EventSettings.objects.get()
        if do_open_drawer:
            self.open_drawer()

        total_sum = 0
        position_lines = list()
        tax_sums = defaultdict(int)
        tax_symbols = dict()

        for position in transaction.positions.all():
            if position.value == 0:
                continue
            total_sum += position.value
            tax_sums[position.tax_rate] += position.tax_value
            if position.tax_rate not in tax_symbols:
                tax_symbols[position.tax_rate] = ascii_uppercase[len(tax_sums)]
            pos_str = ' {product_name} ({tax_str}){gap} {price}'.format(
                position.product.name,
                tax_symbols[position.tax_rate],
                ' ' * (29 - len(position.product.name)),
                self._format_number(position.value),
            )
            position_lines.append(pos_str)
        total_taxes = sum(tax_sums.values())

        if total_sum == 0:
            return

        receipt = str(bytearray([0x1B, 0x61, 1]))
        receipt += settings.receipt_address
        receipt += SEPARATOR
        receipt += POSITION_LIST_HEADER

        receipt += '\r\n'.join(position_lines)
        receipt += SEPARATOR
        receipt += "                      Nettosumme:  {}\r\n".format(self._format_number(total_sum - total_taxes))

        for tax in sorted(list(tax_symbols))[::-1]:
            receipt += "                    MwSt {tax_rate}%% ({tax_identifier}):  {tax_amount}\r\n".format(
                tax_rate=tax,
                tax_identifier=tax_symbols[tax],
                tax_amount=self._format_number(tax_sums[tax]),
            )

        receipt += "                           Summe:  {}\r\n".format(self._format_number(total_sum))
        receipt += settings.receipt_footer + '\r\n'
        receipt += '{} {}\r\n'.format(
            transaction.timestamp.strftime("%d.%m.%Y %H:%M"),
            transaction.session.cashdesk.name,
        )
        receipt += 'Belegnummer: {}\r\n'.format(transaction.pk)
        receipt += '\r\n\r\n'

        try:
            # self.send(image_tools.get_imagedata(settings.STATIC_ROOT + '/' + settings.EVENT_RECIPE_HEADER))
            self.send(receipt)
            self.cut_tape()
        except:
            print(receipt)
            pass


class DummyPrinter:
    def send(self, data):
        pass

    def open_drawer(self):
        pass

    def cut_tape(self):
        pass

    def print_receipt(self, transaction, do_open_drawer=True):
        pass
