from django.views.generic import CreateView, DeleteView, DetailView, ListView

from postix.core.models import Record, RecordEntity


class RecordListView(ListView):
    model = Record
    template_name = 'backoffice/record_list.html'
    context_object_name = 'records'


class RecordCreateView(CreateView):
    model = Record


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
