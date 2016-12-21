from django.core.urlresolvers import reverse
from django.views.generic import FormView

from c6sh.core.models.ping import Ping, generate_ping
from c6sh.troubleshooter.forms import CashdeskForm
from c6sh.troubleshooter.views.utils import TroubleshooterUserRequiredMixin


def get_minutes(timedelta):
    return timedelta.total_seconds() // 60


class PingView(TroubleshooterUserRequiredMixin, FormView):
    template_name = 'troubleshooter/ping.html'
    form_class = CashdeskForm

    def get_context_data(self):
        ctx = super().get_context_data()
        pings = Ping.objects.order_by('pinged')
        ping_count = pings.count()
        ping_success = pings.filter(ponged__isnull=False)
        ping_success_count = ping_success.count()
        loss_percent = '{:.2f}'.format((ping_count - ping_success_count) * 100 / ping_count)

        durations = [get_minutes(p.ponged - p.pinged) for p in ping_success]

        ctx['pings'] = pings
        ctx['ping_success'] = ping_success_count
        ctx['loss_percent'] = loss_percent

        if durations:
            ctx['total_min'] = min(durations)
            ctx['total_max'] = max(durations)
            ctx['total_avg'] = sum(durations) / len(durations)
            ctx['total_mdev'] = sum(((duration - ctx['total_avg']) ** 2) for duration in durations) / len(durations)
        return ctx

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            cashdesk = form.cleaned_data.get('cashdesk')
            generate_ping(cashdesk)
            return self.form_valid(form)

    def get_success_url(self):
        return reverse('troubleshooter:ping')
