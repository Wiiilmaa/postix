from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .utils import TroubleshooterUserRequiredMixin, troubleshooter_user_required
from ...core.models import Cashdesk, Transaction, TransactionPosition
from ...core.utils.flow import reverse_transaction


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
        qs = TransactionPosition.objects.all().select_related('transaction')
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
    pass


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
            reversal_pk = reverse_transaction(pk, session)
            reversal = Transaction.objects.get(pk=reversal_pk)
            reversal.print_receipt(do_open_drawer=False)
            messages.success(request, 'Transaktion wurde storniert ({}). Storno-Bon wurde an {} gedruckt.'.format(reversal_pk, cashdesk))

    return redirect('troubleshooter:transaction-detail', pk=pk)
