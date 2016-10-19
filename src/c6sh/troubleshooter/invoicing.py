from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from c6sh.core.models import EventSettings
from c6sh.core.utils.pdf import (
    CURRENCY, FONTSIZE, get_default_document, get_paragraph_style,
)


def generate_invoice(transaction, address):
    _buffer = BytesIO()
    settings = EventSettings.objects.get()
    doc = get_default_document(_buffer, footer=settings.invoice_footer)
    style = get_paragraph_style()

    # Header
    our_address = settings.invoice_address.replace('\n', '<br />')
    our_address = Paragraph(our_address, style['Normal'])
    our_title = Paragraph('Rechnungsaussteller', style['Heading5'])

    their_address = address.replace('\n', '<br />')
    their_address = Paragraph(their_address, style['Normal'])
    their_title = Paragraph('Rechnungsempfänger', style['Heading5'])

    data = [[their_title, '', our_title], [their_address, '', our_address]]
    header = Table(
        data=data,
        colWidths=[doc.width * 0.3, doc.width * 0.3, doc.width * 0.4],
        style=TableStyle([
            ('FONTSIZE', (0, 0), (2, 1), FONTSIZE),
            ('VALIGN', (0, 0), (2, 1), 'TOP'),
        ]),
    )
    invoice_title = Paragraph('Rechnung {}-{:04d}'.format(settings.short_name, transaction.pk), style['Heading1'])

    data = [['Ticket', 'Steuersatz', 'Netto', 'Brutto'], ]
    total_tax = 0
    for position in transaction.positions.all():
        total_tax += position.tax_value
        data.append([
            position.product.name,
            '{} %'.format(position.tax_rate),
            CURRENCY.format(position.value - position.tax_value,),
            CURRENCY.format(position.value)
        ])
    data.append(['Enthaltene Umsatzsteuer', '', '', CURRENCY.format(total_tax)])
    data.append(['Rechnungsbetrag', '', '', CURRENCY.format(transaction.value)])
    last_row = len(data) - 1

    transaction_table = Table(
        data=data,
        colWidths=[doc.width * 0.5] + [doc.width * 0.5 / 3] * 3,
        style=TableStyle([
            ('FONTSIZE', (0, 0), (3, last_row), FONTSIZE),
            # TODO: register bold font and use here: ('FACE', (0,0), (3,0), 'boldfontname'),
            ('ALIGN', (0, 0), (1, last_row), 'LEFT'),
            ('ALIGN', (2, 0), (3, last_row), 'RIGHT'),
            ('LINEABOVE', (0, 1), (3, 1), 1.0, colors.black),
            ('LINEABOVE', (3, last_row - 1), (3, last_row - 1), 1.0, colors.black),
            ('LINEABOVE', (3, last_row), (3, last_row), 1.2, colors.black),
        ]),
    )

    story = [
        header, Spacer(1, 15 * mm), invoice_title, Spacer(1, 25 * mm), transaction_table,
    ]
    doc.build(story)
    _buffer.seek(0)
    stored_name = default_storage.save(transaction.get_invoice_path(allow_nonexistent=True), ContentFile(_buffer.read()))
    return stored_name
