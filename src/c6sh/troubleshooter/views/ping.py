from django.core.urlresolvers import reverse
from django.views.generic import FormView

from c6sh.core.models.ping import Ping, generate_ping
from c6sh.troubleshooter.forms import CashdeskForm
from c6sh.troubleshooter.views.utils import TroubleshooterUserRequiredMixin


class PingView(TroubleshooterUserRequiredMixin, FormView):
    template_name = 'troubleshooter/ping.html'
    form_class = CashdeskForm

    def get_context_data(self):
        ctx = super().get_context_data()
        ctx['pings'] = Ping.objects.order_by('pinged')
        return ctx

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            cashdesk = form.cleaned_data.get('cashdesk')
            generate_ping(cashdesk)
            return self.form_valid(form)

    def get_success_url(self):
        return reverse('troubleshooter:ping')
