from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.generic import FormView, TemplateView

from postix.backoffice.forms import EventSettingsForm
from postix.backoffice.views.utils import SuperuserRequiredMixin
from postix.core.models import EventSettings, User


class WizardSettingsView(SuperuserRequiredMixin, FormView):
    template_name = 'backoffice/wizard_settings.html'
    form_class = EventSettingsForm

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)

    def get_initial(self):
        settings = EventSettings.get_solo()
        attrs = {
            attr: getattr(settings, attr)
            for attr in EventSettingsForm().fields
        }
        attrs.update({'initialized': True})
        return attrs

    def get_success_url(self):
        return reverse('backoffice:main')


class WizardUsersView(SuperuserRequiredMixin, TemplateView):
    template_name = 'backoffice/wizard_users.html'

    def get_context_data(self):
        ctx = super().get_context_data()
        ctx['users'] = User.objects.order_by('username')
        return ctx

    def post(self, request):
        target = request.POST.get('target')
        pk = request.POST.get('user')
        user = User.objects.get(pk=pk)

        if 'troubleshooter' in target:
            user.is_troubleshooter = target[-1] == 'y'
        elif 'backoffice' in target:
            user.is_backoffice_user = target[-1] == 'y'
        elif 'superuser' in target:
            user.is_superuser = target[-1] == 'y'
        user.save()

        if target[-1] == 'y':
            messages.success(request, _('User rights have been expanded'))
        else:
            messages.success(request, _('User rights have been curtailed.'))
        return redirect('backoffice:wizard-users')
