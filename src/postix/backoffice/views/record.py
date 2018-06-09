from django.contrib.auth import get_user_model
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from postix.backoffice.forms.record import RecordCreateForm
from postix.core.models import Record, RecordEntity

User = get_user_model()


class RecordListView(ListView):
    model = Record
    template_name = 'backoffice/record_list.html'
    context_object_name = 'records'


class RecordCreateView(CreateView):
    model = Record
    form_class = RecordCreateForm
    template_name = 'backoffice/new_record.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['backoffice_users'] = User.objects.filter(is_backoffice_user=True)
        return ctx


class RecordDetailView(DetailView):
    model = Record


class RecordEntityListView(ListView):
    model = RecordEntity


class RecordEntityCreateView(CreateView):
    model = RecordEntity


class RecordEntityDetailView(DetailView):
    model = RecordEntity


class RecordEntityDeleteView(DeleteView):
    model = RecordEntity
