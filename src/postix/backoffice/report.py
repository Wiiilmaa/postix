from io import BytesIO
from tempfile import TemporaryFile

import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, Spacer, Table, TableStyle

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


def get_session_header(session, doc, title='Kassenbericht'):
    style = get_paragraph_style()
    settings = EventSettings.get_solo()
    title_str = '[{}] {}'.format(settings.short_name, title)
    title = Paragraph(title_str, style['Heading1'])
    tz = timezone.get_current_timezone()
    text = '{} an '.format(session.user.get_full_name() if session.user else '')
    text += "{cashdesk} (#{pk})<br/>{start} – {end}".format(
        cashdesk=session.cashdesk,
        pk=session.pk,
        start=session.start.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
        end=session.end.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
    )
    info = Paragraph(text, style['Normal'])

    return Table(
        data=[[[title, info], ''], ],
        colWidths=[doc.width / 2] * 2,
        style=TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (1, 0), 'TOP'),
        ]),
    )


def get_signature_block(names, doc):
    col_width = (doc.width - 35) / 2
    second_sig = 2 if names[1] else 0
    return Table(
        data=[[names[0], '', names[1]]],
        colWidths=[col_width, 35, col_width],
        style=TableStyle([
            ('FONTSIZE', (0, 0), (2, 0), FONTSIZE),
            ('LINEABOVE', (0, 0), (0, 0), 1.2, colors.black),
            ('LINEABOVE', (second_sig, 0), (second_sig, 0), 1.2, colors.black),
            ('VALIGN', (0, 0), (2, 0), 'TOP'),
        ]),
    )


def generate_item_report(session: CashdeskSession, doc) -> str:
    """
    Generates a closing report for a CashdeskSession that handled items
    """
    if not session.end:
        return

    style = get_paragraph_style()

    header = get_session_header(session, doc)

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
    settings = EventSettings.get_solo()
    doc = get_default_document(_buffer, footer=settings.report_footer)
    style = get_paragraph_style()

    # Header: info text and qr code
    title_str = '[{}] {}beleg'.format(settings.short_name, 'Einnahme' if record.type == 'inflow' else 'Ausgabe')
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
    name = record.named_entity
    if record.cash_movement and record.cash_movement.session:
        name += ' (#{})'.format(record.cash_movement.session.pk)
    info = [
        ['Datum', datetime.strftime('%Y-%m-%d, %H:%M')],
        ['Von' if record.type == 'inflow' else 'Nach', name],
        ['Betrag', CURRENCY.format(record.amount)]
    ]
    info = [
        [Paragraph('<b>{}</b>'.format(line[0]), style['Normal']), Paragraph(line[1], style['Normal'])]
        for line in info
    ]

    info_table = Table(
        data=info,
        colWidths=[90, doc.width - 90],
        style=TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ]),
    )

    # Signatures
    signature1 = get_signature_block(
        ['Bearbeiter/in: {}'.format(record.backoffice_user.get_full_name()), ''],
        doc=doc,
    )

    story = [
        header, Spacer(1, 15 * mm),
        info_table, Spacer(1, 40 * mm),
        signature1,
    ]
    if record.named_carrier:
        story.append(Spacer(1, 40 * mm))
        story.append(get_signature_block(['{}: {}'.format('Einlieferer/in' if record.type == 'inflow' else 'Emfpänger/in', record.carrier or ''), ''], doc=doc))
    if record.cash_movement and record.closes_session:
        if record.cash_movement.session.cashdesk.handles_items:
            story.append(PageBreak())
            story += generate_item_report(record.cash_movement.session, doc=doc)
        story.append(PageBreak())
        story += generate_session_closing(record, doc=doc)

    doc.build(story)
    _buffer.seek(0)
    stored_name = default_storage.save(record.get_new_record_path(), ContentFile(_buffer.read()))
    return stored_name
