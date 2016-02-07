from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import PreorderSerializer, PreorderPositionSerializer
from ..core.models import Preorder, PreorderPosition


class PreorderViewSet(ReadOnlyModelViewSet):
    """
    This is a read-only list of all preorders.
    """
    queryset = Preorder.objects.all()
    serializer_class = PreorderSerializer


class PreorderPositionViewSet(ReadOnlyModelViewSet):
    """
    This is a read-only list of all preorder positions.

    You can filter using query parameters by the ``secret`` field. You can also
    search for secrets by using the ``?search=`` query parameter, that will only
    match the *beginning* of secrets and only if the search query has more than
    6 characters.
    """
    queryset = PreorderPosition.objects.all()
    serializer_class = PreorderPositionSerializer
    filter_fields = ('secret',)

    def get_queryset(self):
        queryset = PreorderPosition.objects.all()
        search_param = self.request.query_params.get('search', None)
        if search_param is not None and len(search_param) >= 6:
            queryset = queryset.filter(secret__startswith=search_param)
        return queryset