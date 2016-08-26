import tempfile
from io import BytesIO

import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from reportlab.lib import colors, utils
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, PageTemplate, Paragraph, Spacer, Table,
    TableStyle,
)

from c6sh.core.models import EventSettings


FONTSIZE = 11
PAGESIZE = portrait(A4)
CUR = '{:.2f} €'


def get_paragraph_style():
    style = getSampleStyleSheet()
    # TODO: font
    # style.fontName = 'OpenSans'
    style['Normal'].fontSize = FONTSIZE
    style['Normal'].leading = int(1.5 * FONTSIZE)
    return style


def get_image(fileish, width):
    """ scales image with given width. fileish may be file or path """
    img = utils.ImageReader(fileish)
    orig_width, height = img.getSize()
    aspect = height / orig_width
    return Image(fileish, width=width, height=width * aspect)


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
        supervisor='{u.firstname} {u.lastname}'.format(u=session.backoffice_user_after),
        user='{u.firstname} {u.lastname}'.format(u=session.user),
    )
    qr.add_data(data)
    qr.make()

    f = tempfile.TemporaryFile()
    img = qr.make_image()
    img.save(f)
    return f


def get_default_document(buffer):
    def on_page(canvas, doc):
        footer = EventSettings.objects.get().report_footer
        canvas.saveState()
        canvas.setFontSize(8)
        for i, line in enumerate(footer.split('\n')[::-1]):
            canvas.drawCentredString(PAGESIZE[0] / 2, 25 + (3.5 * i) * mm, line.strip())
        canvas.restoreState()

    doc = BaseDocTemplate(
        buffer,
        pagesize=PAGESIZE,
        leftMargin=25 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='normal')
    doc_template = PageTemplate(id='all', pagesize=PAGESIZE, frames=[frame], onPage=on_page)
    doc.addPageTemplates([doc_template])
    return doc


def generate_report(session):
    buffer = BytesIO()
    doc = get_default_document(buffer)
    style = get_paragraph_style()

    # Header: info text and qr code
    title_str = '[{}] Kassenbericht #{}'.format(EventSettings.objects.get().short_name, session.pk)
    title = Paragraph(title_str, style['Heading1'])
    text = """{session.user.firstname} {session.user.lastname} an {session.cashdesk}<br/>{date} {start} bis {end}""".format(
        session=session,
        date=session.start.date(),
        start=session.start.replace(microsecond=0).time(),
        end=session.end.replace(microsecond=0).time(),
    )
    info = Paragraph(text, style['Normal'])
    logo = get_image(get_qr_image(session), 100)

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
             CUR.format(p['value_single']), CUR.format(p['value_total'])]
             for p in sales_raw_data]
    data += sales
    data += [['', '', '', '', '', CUR.format(sum([p['value_total'] for p in sales_raw_data]))]]
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
             CUR.format(session.cash_before),
             CUR.format(cash_transactions),
             CUR.format(session.cash_after),
             CUR.format(session.cash_before + cash_transactions - session.cash_after)], ]
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
        data=[['Kassierer/in: {} {}'.format(session.user.firstname, session.user.lastname), '',
               'Ausgezählt durch {} {}'.format(session.backoffice_user_after.firstname, session.backoffice_user_after.lastname)]],
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

    buffer.seek(0)
    stored_name = default_storage.save(session.get_new_report_path(), ContentFile(buffer.read()))
    return stored_name
