from django.core.urlresolvers import reverse
from django.views.generic import FormView

from c6sh.backoffice.forms import EventSettingsForm
from c6sh.backoffice.views.utils import BackofficeUserRequiredMixin
from c6sh.core.models import EventSettings


class WizardSettingsView(BackofficeUserRequiredMixin, FormView):
    template_name = 'backoffice/wizard_settings.html'
    form_class = EventSettingsForm

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)

    def get_initial(self):
        settings = EventSettings.objects.get_solo()
        attrs = {
            attr: getattr(settings, attr)
            for attr in EventSettingsForm().fields
        }
        attrs.update({'initialized': True})
        return attrs

    def get_success_url(self):
        return reverse('backoffice:main')
