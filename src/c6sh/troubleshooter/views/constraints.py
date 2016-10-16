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
