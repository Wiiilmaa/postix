from django.db.models import Sum
from django.views.generic import TemplateView

from c6sh.core.models.base import Item, TransactionPositionItem

from .. import checks
from .utils import BackofficeUserRequiredMixin


class MainView(BackofficeUserRequiredMixin, TemplateView):
    template_name = 'backoffice/main.html'

    def get_context_data(self):
        ctx = super().get_context_data()
        data = dict()
        qs = TransactionPositionItem.objects.filter(
            position__reversed_by__isnull=True,
            position__type__in=['redeem', 'sell']
        )
        for item in Item.objects.all():
            data[item.name] = qs.filter(item=item).aggregate(total=Sum('amount'))['total']
        ctx['data'] = data
        ctx['check_errors'] = checks.all_errors()
        return ctx
