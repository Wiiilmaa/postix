from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView

from ...core.models import Preorder
from .utils import TroubleshooterUserRequiredMixin


class PreorderListView(TroubleshooterUserRequiredMixin, ListView):
    template_name = 'troubleshooter/preorders.html'
    context_object_name = 'preorders'
    model = Preorder

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.filter = dict()
        _filter = self.request.GET
        if 'code' in _filter and _filter['code']:
            if len(_filter['code']) < 4:
                messages.error(request, _('You need to enter at least four characters of the order code.'))
            else:
                self.filter['code'] = _filter['code']
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        qs = Preorder.objects.all().order_by('order_code')
        if 'code' in self.filter:
            qs = qs.filter(order_code__icontains=self.filter['code'])
        else:
            qs = qs.none()
        return qs


class PreorderDetailView(TroubleshooterUserRequiredMixin, DetailView):
    template_name = 'troubleshooter/preorder_detail.html'
    context_object_name = 'preorder'
    model = Preorder
