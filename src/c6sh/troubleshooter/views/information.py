from django.views.generic.list import ListView

from c6sh.core.models import Info
from .utils import TroubleshooterUserRequiredMixin


class InformationListView(TroubleshooterUserRequiredMixin, ListView):
    template_name = 'troubleshooter/information_list.html'
    context_object_name = 'information'
    paginate_by = 50
    model = Info
