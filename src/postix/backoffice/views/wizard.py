from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.generic import FormView, ListView, TemplateView, UpdateView

from postix.backoffice.forms import (
    CashdeskForm, EventSettingsForm, ImportForm, ItemForm,
)
from postix.backoffice.views.utils import SuperuserRequiredMixin
from postix.core.models import EventSettings, Item, User


class WizardSettingsView(SuperuserRequiredMixin, FormView):
    template_name = 'backoffice/wizard_settings.html'
    form_class = EventSettingsForm

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, _('The settings have been updated \o/'))
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
        return reverse('backoffice:wizard-settings')


class WizardCashdesksView(SuperuserRequiredMixin, FormView):
    template_name = 'backoffice/wizard_cashdesks.html'
    form_class = CashdeskForm

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, _('The cashdesk has been created \o/'))
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
        return reverse('backoffice:wizard-cashdesks')


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


class WizardPretixImportView(SuperuserRequiredMixin, FormView):
    template_name = 'backoffice/wizard_import.html'
    form_class = ImportForm

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            from postix.core.utils.pretix_import import import_pretix_data
            try:
                pretix_import = request.FILES['_file']
                import_pretix_data(
                    pretix_import.read().decode(),
                    add_cashdesks=form.cleaned_data['cashdesks'],
                    questions=form.cleaned_data['questions'],
                )
                messages.success(request, _('The import has been processed \\o/'))
            except Exception as e:
                messages.error(request, _('The import could not be processed: ') + str(e))
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
        return reverse('backoffice:wizard-import')


class WizardItemListView(SuperuserRequiredMixin, ListView):
    template_name = 'backoffice/wizard_item_list.html'
    model = Item


class WizardItemCreateView(SuperuserRequiredMixin, FormView):
    template_name = 'backoffice/wizard_item_edit.html'
    form_class = ItemForm

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, _('The item has been saved \o/'))
            return self.form_valid(form)

    def get_success_url(self):
        return reverse('backoffice:wizard-items-list')


class WizardItemEditView(SuperuserRequiredMixin, UpdateView):
    template_name = 'backoffice/wizard_item_edit.html'
    model = Item
    form_class = ItemForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('The item has been updated \o/'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('backoffice:wizard-items-list')
