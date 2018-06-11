from io import BytesIO
from tempfile import TemporaryFile

import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from postix.core.models import CashdeskSession, EventSettings, Record
from postix.core.utils.pdf import (
    CURRENCY, FONTSIZE, get_default_document, get_paragraph_style, scale_image,
)


def get_qr_image(session: CashdeskSession) -> TemporaryFile:
    # TODO: check qr code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    tz = timezone.get_current_timezone()
    if isinstance(session, CashdeskSession):
        data = '{end}\tEinnahme\t{total}\tKassensession\t#{pk}\t{supervisor}\t{user}'.format(
            end=session.end.astimezone(tz).strftime('%d.%m.%Y\t%H:%M:%S'),
            total='{0:,.2f}'.format(session.get_cash_transaction_total()).translate(str.maketrans(',.', '.,')),
            pk=session.pk,
            supervisor=session.backoffice_user_after.get_full_name(),
            user=session.user.get_full_name(),
        )
    else:
        data = '{end}\t{direction}\t{total}\t{entity}\t{supervisor}\t{user}'.format(
            end=session.datetime.astimezone(tz).strftime('%d.%m.%Y\t%H:%M:%S'),
            direction='Einnahme' if session.type == 'inflow' else 'Ausgabe',
            total='{0:,.2f}'.format(session.amount).translate(str.maketrans(',.', '.,')),
            entity='{e.name}\t{e.detail}'.format(e=session.entity),
            supervisor=session.backoffice_user.get_full_name(),
            user=session.carrier or '',
        )
    qr.add_data(data)
    qr.make()

    f = TemporaryFile()
    img = qr.make_image()
    img.save(f)
    return f


def generate_report(session: CashdeskSession) -> str:
    """
    Generates a closing report for a CashdeskSession; returns the path to the
    report PDF.
    """
    _buffer = BytesIO()
    doc = get_default_document(_buffer, footer=EventSettings.objects.get().report_footer)
    style = get_paragraph_style()

    # Header: info text and qr code
    title_str = '[{}] Kassenbericht #{}'.format(EventSettings.objects.get().short_name, session.pk)
    title = Paragraph(title_str, style['Heading1'])
    tz = timezone.get_current_timezone()
    text = """{user} an {cashdesk}<br/>{start} – {end}""".format(
        user=session.user.get_full_name(),
        cashdesk=session.cashdesk,
        start=session.start.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
        end=session.end.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
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
    data = [['Ticket', 'Einzelpreis', 'Presale', 'Verkauf', 'Stornos', 'Gesamt'], ]
    sales_raw_data = session.get_product_sales()
    sales = [[p['product'].name, CURRENCY.format(p['value_single']), p['presales'], p['sales'],
              p['reversals'], CURRENCY.format(p['value_total'])]
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
    items = [
        [d['item'].name, d['movements'], d['transactions'], abs(d['final_movements']), d['total']]
        for d in session.get_current_items()
    ]
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


def generate_record(record: Record) -> str:
    """
    Generates the PDF for a given record; returns the path to the record PDF.
    """
    _buffer = BytesIO()
    doc = get_default_document(_buffer, footer=EventSettings.objects.get().report_footer)
    style = get_paragraph_style()

    # Header: info text and qr code
    title_str = '[{}] {}beleg'.format(EventSettings.objects.get().short_name, 'Einnahme' if record.type == 'inflow' else 'Ausgabe')
    title = Paragraph(title_str, style['Heading1'])
    tz = timezone.get_current_timezone()
    datetime = record.datetime.astimezone(tz)
    logo = scale_image(get_qr_image(record), 100)
    header = Table(
        data=[[[title, ], logo], ],
        colWidths=[doc.width / 2] * 2,
        style=TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (1, 0), 'TOP'),
        ]),
    )
    info = [
        ['Datum', datetime.strftime('%Y-%m-%d, %H:%M')],
        ['Von' if record.type == 'inflow' else 'Nach', str(record.entity)],
        ['Betrag', CURRENCY.format(record.amount)]
    ]
    info = [
        [Paragraph(line[0], style['Heading3']), Paragraph(line[1], style['Normal'])]
        for line in info
    ]

    info_table = Table(
        data=info,
        colWidths=[90, doc.width - 90],
        style=TableStyle([
        ]),
    )

    # Signatures
    col_width = (doc.width - 35) / 2
    signature1 = Table(
        data=[['Bearbeiter/in: {}'.format(record.backoffice_user.get_full_name()), '', '']],
        colWidths=[col_width, 35, col_width],
        style=TableStyle([
            ('FONTSIZE', (0, 0), (0, 0), FONTSIZE),
            ('LINEABOVE', (0, 0), (0, 0), 1.2, colors.black),
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ]),
    )
    if record.carrier:
        signature2 = Table(
            data=[['{}: {}'.format('Einlieferer/in' if record.type == 'inflow' else 'Emfpänger/in', record.carrier), '', '']],
            colWidths=[col_width, 35, col_width],
            style=TableStyle([
                ('FONTSIZE', (0, 0), (0, 0), FONTSIZE),
                ('LINEABOVE', (0, 0), (0, 0), 1.2, colors.black),
                ('VALIGN', (0, 0), (0, 0), 'TOP'),
            ]),
        )

    story = [
        header, Spacer(1, 15 * mm),
        info_table, Spacer(1, 40 * mm),
        signature1,
    ]
    if record.carrier:
        story.append(Spacer(1, 40 * mm))
        story.append(signature2)
    doc.build(story)

    _buffer.seek(0)
    stored_name = default_storage.save(record.get_new_record_path(), ContentFile(_buffer.read()))
    return stored_name
