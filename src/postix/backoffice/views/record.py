from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, ListView, TemplateView, UpdateView,
)

from postix.backoffice.forms.record import (
    RecordCreateForm, RecordEntityForm, RecordUpdateForm,
)
from postix.backoffice.report import generate_record
from postix.core.models import Record, RecordEntity

from .utils import (
    BackofficeUserRequiredMixin, SuperuserRequiredMixin,
    backoffice_user_required,
)

User = get_user_model()


class RecordListView(BackofficeUserRequiredMixin, TemplateView):
    model = Record
    template_name = 'backoffice/record_list.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        records = Record.objects.all()
        running_total = 0
        for obj in records:
            if obj.type == 'inflow':
                running_total += obj.amount
            else:
                running_total -= obj.amount
            obj.running_total = running_total
        ctx['records'] = records[::-1]
        return ctx


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
        return reverse(
            'backoffice:record-print', kwargs={'pk': self.get_form().instance.pk}
        )


class RecordDetailView(BackofficeUserRequiredMixin, UpdateView):
    model = Record
    form_class = RecordUpdateForm
    template_name = 'backoffice/record_detail.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['backoffice_users'] = User.objects.filter(is_backoffice_user=True)
        ctx['carriers'] = set(Record.objects.all().values_list('carrier', flat=True))
        return ctx

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['editable'] = 'edit' in self.request.GET
        return kwargs

    def get_success_url(self):
        return reverse('backoffice:record-print', kwargs={'pk': self.kwargs['pk']})


@backoffice_user_required
def record_print(request, pk: int):
    record = get_object_or_404(Record, pk=pk)

    if (
        not record.record_path or 'cached' not in request.GET
    ):  # TODO: don't regenerate pdf always
        generate_record(record)

    response = HttpResponse(content=default_storage.open(record.record_path, 'rb'))
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'inline; filename=record-{}.pdf'.format(record.pk)
    return response


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
