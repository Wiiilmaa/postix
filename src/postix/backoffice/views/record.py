from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from postix.backoffice.forms.record import RecordCreateForm, RecordEntityForm
from postix.core.models import Record, RecordEntity

from .utils import BackofficeUserRequiredMixin, SuperuserRequiredMixin

User = get_user_model()


class RecordListView(BackofficeUserRequiredMixin, ListView):
    model = Record
    template_name = 'backoffice/record_list.html'
    context_object_name = 'records'


class RecordCreateView(BackofficeUserRequiredMixin, CreateView):
    model = Record
    form_class = RecordCreateForm
    template_name = 'backoffice/new_record.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['backoffice_users'] = User.objects.filter(is_backoffice_user=True)
        ctx['carriers'] = set(Record.objects.all().values_list('carrier', flat=True))
        return ctx

    def get_success_url(self):
        return reverse('backoffice:record-list')


class RecordDetailView(BackofficeUserRequiredMixin, UpdateView):
    model = Record


class RecordEntityListView(SuperuserRequiredMixin, ListView):
    model = RecordEntity
    template_name = 'backoffice/record_entity_list.html'
    context_object_name = 'entities'


class RecordEntityCreateView(SuperuserRequiredMixin, CreateView):
    model = RecordEntity
    form_class = RecordEntityForm
    template_name = 'backoffice/new_record_entity.html'

    def get_success_url(self):
        return reverse('backoffice:record-entity-list')


class RecordEntityDetailView(SuperuserRequiredMixin, UpdateView):
    model = RecordEntity
    form_class = RecordEntityForm
    template_name = 'backoffice/new_record_entity.html'

    def get_success_url(self):
        return reverse('backoffice:record-entity-list')


class RecordEntityDeleteView(SuperuserRequiredMixin, DeleteView):
    model = RecordEntity
    template_name = 'backoffice/delete_record_entity.html'
    context_object_name = 'record'

    def get_success_url(self):
        return reverse('backoffice:record-entity-list')
