from django.db.models import Q
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .utils import TroubleshooterUserRequiredMixin
from ...core.models import ListConstraint


class ListConstraintListView(TroubleshooterUserRequiredMixin, ListView):
    template_name = 'troubleshooter/constraints_list.html'
    context_object_name = 'constraints'
    model = ListConstraint


class ListConstraintDetailView(TroubleshooterUserRequiredMixin, DetailView):
    template_name = 'troubleshooter/constraint_detail.html'
    context_object_name = 'constraint'
    model = ListConstraint

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = kwargs['object']

        if self.request.GET and self.request.GET['filter'] and self.request.GET['filter'][0]:
            query = self.request.GET['filter'][0]
            ctx['entries'] = obj.entries.filter(
                Q(name__icontains=query) | Q(identifier__icontains=query)
            )
        else:
            ctx['entries'] = obj.entries.all()
        return ctx
