from django.views.generic.list import ListView

from .utils import TroubleshooterUserRequiredMixin
from ...core.models import Cashdesk, Transaction, TransactionPosition


class TransactionListView(TroubleshooterUserRequiredMixin, ListView):
    template_name = 'troubleshooter/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        self.filter = dict()
        _filter = self.request.GET

        if 'type' in _filter:
            print(_filter['type'])
            self.filter['type'] = [
                request_filter for request_filter in _filter['type']
                if request_filter in (t[0] for t in TransactionPosition.TYPES)
            ]
                
        if 'desk' in _filter:
            try:
                desk = Cashdesk.objects.get(pk=_filter['cashdesk'])
                self.filter['cashdesk'] = desk
            except Cashdesk.DoesNotExist:
                pass
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = TransactionPosition.objects.all().select_related('transaction')
        if 'cashdesk' in self.filter:
            qs = qs.filter(transaction__cashdesk=self.filter['cashdesk'])
        if 'type' in self.filter and self.filter['type']:
            qs = qs.filter(type__in=self.filter['type'])
        return qs
