from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from ...core.models import Cashdesk, Transaction, TransactionPosition
from ...core.utils.flow import (
    reverse_transaction, reverse_transaction_position,
)
from ..forms import InvoiceAddressForm
from ..invoicing import generate_invoice
from .utils import (
    TroubleshooterUserRequiredMixin, troubleshooter_user_required,
)


class TransactionListView(TroubleshooterUserRequiredMixin, ListView):
    template_name = 'troubleshooter/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        self.filter = dict()
        _filter = self.request.GET
        types = [t[0] for t in TransactionPosition.TYPES]

        if 'type' in _filter and _filter['type'] in types:
            self.filter['type'] = _filter['type']

        if 'desk' in _filter and _filter['desk']:
            try:
                desk = Cashdesk.objects.get(pk=_filter['desk'])
                self.filter['cashdesk'] = desk
            except Cashdesk.DoesNotExist:
                pass
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = TransactionPosition.objects.all()\
            .order_by('-transaction__datetime')\
            .select_related('transaction')
        if 'cashdesk' in self.filter:
            qs = qs.filter(transaction__session__cashdesk=self.filter['cashdesk'])
        if 'type' in self.filter and self.filter['type']:
            qs = qs.filter(type=self.filter['type'])
        return qs

    def get_context_data(self):
        ctx = super().get_context_data()
        ctx['cashdesks'] = Cashdesk.objects.all()
        ctx['types'] = [t[0] for t in TransactionPosition.TYPES]
        return ctx


class TransactionDetailView(TroubleshooterUserRequiredMixin, DetailView):
    template_name = 'troubleshooter/transaction_detail.html'
    context_object_name = 'transaction'
    model = Transaction


@troubleshooter_user_required
def transaction_reprint(request, pk):
    if request.method == 'POST':
        try:
            transaction = Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            messages.error(request, 'Transaktion nicht bekannt.')
        else:
            transaction.print_receipt(do_open_drawer=False)
            messages.success(request, 'Bon wurde an {} neu gedruckt.'.format(transaction.session.cashdesk))

    return redirect('troubleshooter:transaction-detail', pk=pk)


@troubleshooter_user_required
def transaction_invoice(request, pk):
    def return_invoice(path, pk=pk):
        response = HttpResponse(content=default_storage.open(path, 'rb'))
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = 'inline; filename=invoice-{}.pdf'.format(pk)
        return response

    try:
        transaction = Transaction.objects.get(pk=pk)
    except:
        messages.error('Transaktion nicht bekannt')
        return redirect('troubleshooter:transaction-list')

    path = transaction.get_invoice_path()
    if path:
        return return_invoice(path)

    form = InvoiceAddressForm()
    if request.method == 'POST':
        form = InvoiceAddressForm(request.POST)
        if form.is_valid():
            path = generate_invoice(transaction, form.cleaned_data['address'])
            return return_invoice(path)
        else:
            messages(form.errors)

    return render(request, 'troubleshooter/invoice.html', {'form': form})


@troubleshooter_user_required
def transaction_position_cancel(request, pk):
    try:
        position = TransactionPosition.objects.get(pk=pk)
    except TransactionPosition.DoesNotExist:
        messages.error(request, 'Transaktionszeile nicht bekannt.')
    else:
        if request.method == 'POST':
            cashdesk = position.transaction.session.cashdesk
            session = cashdesk.get_active_sessions()[0]
            reversal_pk = reverse_transaction_position(pk, session, authorized_by=request.user)
            reversal = Transaction.objects.get(pk=reversal_pk)
            reversal.print_receipt(do_open_drawer=False)
            messages.success(request, 'Transaktionszeile wurde storniert ({}). Storno-Bon wurde an {} gedruckt.'.format(reversal_pk, cashdesk))

    return redirect('troubleshooter:transaction-detail', pk=position.transaction.pk)


@troubleshooter_user_required
def transaction_cancel(request, pk):
    if request.method == 'POST':
        try:
            transaction = Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            messages.error(request, 'Transaktion nicht bekannt.')
        else:
            cashdesk = transaction.session.cashdesk
            session = cashdesk.get_active_sessions()[0]
            reversal_pk = reverse_transaction(pk, session, authorized_by=request.user)
            reversal = Transaction.objects.get(pk=reversal_pk)
            reversal.print_receipt(do_open_drawer=False)
            messages.success(request, 'Transaktion wurde storniert ({}). Storno-Bon wurde an {} gedruckt.'.format(reversal_pk, cashdesk))

    return redirect('troubleshooter:transaction-detail', pk=pk)
