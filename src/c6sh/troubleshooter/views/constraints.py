from django.views.generic.list import ListView

from .utils import TroubleshooterUserRequiredMixin
from ...core.models import ListConstraint


class ListConstraintListView(TroubleshooterUserRequiredMixin, ListView):
    template_name = 'troubleshooter/constraints_list.html'
    context_object_name = 'constraints'
    queryset = ListConstraint.objects.all()
