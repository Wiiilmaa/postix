from django.views.generic import TemplateView

from postix.core.models.base import Item, Product
from postix.core.models.cashdesk import CashdeskSession

from .. import checks
from .utils import BackofficeUserRequiredMixin


class MainView(BackofficeUserRequiredMixin, TemplateView):
    template_name = 'backoffice/main.html'

    def get_context_data(self):
        ctx = super().get_context_data()
        ctx['products'] = Product.objects.all()
        ctx['items'] = Item.objects.all()
        ctx['money'] = sum(c.cash_before for c in CashdeskSession.active.all())
        ctx['check_errors'] = checks.all_errors()
        return ctx
