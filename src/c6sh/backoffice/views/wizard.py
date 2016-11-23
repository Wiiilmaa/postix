from django.core.urlresolvers import reverse
from django.views.generic import FormView

from c6sh.backoffice.forms import EventSettingsForm
from c6sh.backoffice.views.utils import BackofficeUserRequiredMixin


class WizardSettingsView(BackofficeUserRequiredMixin, FormView):
    template_name = 'backoffice/wizard_settings.html'
    form_class = EventSettingsForm

    def get_success_url(self):
        return reverse('backoffice:main')
