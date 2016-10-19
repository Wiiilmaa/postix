import tempfile
from io import BytesIO

import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from c6sh.core.models import EventSettings
from c6sh.core.utils.pdf import (
    CURRENCY, FONTSIZE, get_default_document, get_paragraph_style, scale_image,
)


def get_qr_image(session):
    # TODO: check qr code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    data = '{end}\tEinnahme\t{total}\tKassensession\t#{pk}\t{supervisor}\t{user}'.format(
        end=session.end.strftime('%d.%m.%Y\t%H:%M:%S'),
        total='{0:,.2f}'.format(session.get_cash_transaction_total()).translate(str.maketrans(',.', '.,')),
        pk=session.pk,
        supervisor=session.backoffice_user_after.get_full_name(),
        user=session.user.get_full_name(),
    )
    qr.add_data(data)
    qr.make()

    f = tempfile.TemporaryFile()
    img = qr.make_image()
    img.save(f)
    return f


def generate_report(session):
    _buffer = BytesIO()
    doc = get_default_document(_buffer, footer=EventSettings.objects.get().report_footer)
    style = get_paragraph_style()

    # Header: info text and qr code
    title_str = '[{}] Kassenbericht #{}'.format(EventSettings.objects.get().short_name, session.pk)
    title = Paragraph(title_str, style['Heading1'])
    text = """{user} an {cashdesk}<br/>{start} – {end}""".format(
        user=session.user.get_full_name(),
        cashdesk=session.cashdesk,
        start=session.start.strftime('%Y-%m-%d %H:%M:%S'),
        end=session.end.strftime('%Y-%m-%d %H:%M:%S'),
    )
    info = Paragraph(text, style['Normal'])
    logo = scale_image(get_qr_image(session), 100)

    header = Table(
        data=[[[title, info], logo], ],
        colWidths=[doc.width / 2] * 2,
        style=TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (1, 0), 'TOP'),
        ]),
    )

    # Sales table
    sales_heading = Paragraph('Tickets', style['Heading3'])
    data = [['Ticket', 'Presale', 'Verkauf', 'Stornos', 'Einzelpreis', 'Gesamt'], ]
    sales_raw_data = session.get_product_sales()
    sales = [[p['product'].name, p['presales'], p['sales'], p['reversals'],
             CURRENCY.format(p['value_single']), CURRENCY.format(p['value_total'])]
             for p in sales_raw_data]
    data += sales
    data += [['', '', '', '', '', CURRENCY.format(sum([p['value_total'] for p in sales_raw_data]))]]
    last_row = len(data) - 1
    sales = Table(
        data=data,
        colWidths=[120] + [(doc.width - 120) / 5] * 5,
        style=TableStyle([
            ('FONTSIZE', (0, 0), (5, last_row), FONTSIZE),
            # TODO: register bold font and use here: ('FACE', (0,0), (3,0), 'boldfontname'),
            ('ALIGN', (0, 0), (0, last_row), 'LEFT'),
            ('ALIGN', (1, 0), (5, last_row), 'RIGHT'),
            ('LINEABOVE', (0, 1), (5, 1), 1.0, colors.black),
            ('LINEABOVE', (5, last_row), (5, last_row), 1.2, colors.black),
        ]),
    )

    # Items table
    items_heading = Paragraph('Auszählung', style['Heading3'])
    data = [['', 'Einzählung', 'Umsatz', 'Auszählung', 'Differenz'], ]

    # geld immer decimal mit € und nachkommastellen
    cash_transactions = session.get_cash_transaction_total()
    cash = [['Bargeld',
             CURRENCY.format(session.cash_before),
             CURRENCY.format(cash_transactions),
             CURRENCY.format(session.cash_after),
             CURRENCY.format(session.cash_before + cash_transactions - session.cash_after)], ]
    items = [[d['item'].name, d['movements'], d['transactions'], abs(d['final_movements']), d['total']] for d in session.get_current_items()]
    last_row = len(items) + 1
    items = Table(
        data=data + cash + items,
        colWidths=[120] + [(doc.width - 120) / 4] * 4,
        style=TableStyle([
            ('FONTSIZE', (0, 0), (4, last_row), FONTSIZE),
            # TODO: register bold font and use here: ('FACE', (0,0), (3,0), 'boldfontname'),
            ('ALIGN', (0, 0), (0, last_row), 'LEFT'),
            ('ALIGN', (1, 0), (4, last_row), 'RIGHT'),
            ('LINEABOVE', (0, 1), (4, 1), 1.0, colors.black),
        ]),
    )

    # Signatures
    col_width = (doc.width - 35) / 2
    signatures = Table(
        data=[['Kassierer/in: {}'.format(session.user.get_full_name()), '',
               'Ausgezählt durch {}'.format(session.backoffice_user_after.get_full_name())]],
        colWidths=[col_width, 35, col_width],
        style=TableStyle([
            ('FONTSIZE', (0, 0), (2, 0), FONTSIZE),
            ('LINEABOVE', (0, 0), (0, 0), 1.2, colors.black),
            ('LINEABOVE', (2, 0), (2, 0), 1.2, colors.black),
            ('VALIGN', (0, 0), (2, 0), 'TOP'),
        ]),
    )

    story = [
        header, Spacer(1, 15 * mm),
        sales_heading, sales, Spacer(1, 10 * mm),
        items_heading, items, Spacer(1, 30 * mm),
        signatures,
    ]
    doc.build(story)

    _buffer.seek(0)
    stored_name = default_storage.save(session.get_new_report_path(), ContentFile(_buffer.read()))
    return stored_name
