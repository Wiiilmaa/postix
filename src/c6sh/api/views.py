from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ReadOnlyModelViewSet

from django.db.models import Q

from .serializers import PreorderSerializer, PreorderPositionSerializer, ListConstraintSerializer, ListConstraintEntrySerializer, TransactionSerializer
from ..core.models import Preorder, PreorderPosition, ListConstraint, ListConstraintEntry, Transaction

class PreorderViewSet(ReadOnlyModelViewSet):
    """
    This is a read-only list of all preorders.
    """
    queryset = Preorder.objects.all()
    serializer_class = PreorderSerializer
    permission_classes = (IsAdminUser,)


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
        else:
            queryset = queryset.none()
        return queryset

class TransactionViewSet(ReadOnlyModelViewSet):
    """
    This is a list of all transactions.
    """
    queryset = Transaction.objects.all().prefetch_related('positions')
    serializer_class = TransactionSerializer


class ListConstraintViewSet(ReadOnlyModelViewSet):

    queryset = ListConstraint.objects.all()
    serializer_class = ListConstraintSerializer

class ListConstraintEntryViewSet(ReadOnlyModelViewSet):

    queryset = ListConstraintEntry.objects.all()
    serializer_class = ListConstraintEntrySerializer

    def get_queryset(self):
        queryset = ListConstraintEntry.objects.all()
        listid_param = self.request.query_params.get('listid', None)
        if listid_param is not None:
            queryset = queryset.filter(list_id=listid_param)
            search_param = self.request.query_params.get('search', None)
            if search_param is not None and len(search_param) >= 3:
                queryset = queryset.filter(Q(name__contains=search_param)|Q(identifier__contains=search_param))
            else:
                queryset = queryset.none()
        return queryset