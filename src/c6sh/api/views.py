from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import (
    PreorderSerializer, PreorderPositionSerializer, ListConstraintSerializer,
    ListConstraintEntrySerializer, TransactionSerializer
)
from ..core.models import Preorder, PreorderPosition, ListConstraint, ListConstraintEntry, Transaction
from ..core.utils.flow import FlowError, redeem_preorder_ticket
from ..core.utils import round_decimal


class ProcessException(Exception):
    def __init__(self, data):
        self.data = data


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
    This is a list of all transactions. It is also the endpoint you will use to
    create a new transaction.

    Creating transactions
    ---------------------
    To create a transaction, you have to ``POST`` a JSON document to this endpoint
    that matches the following form:

        {
            "cash_given": "12.00",
            "positions": [
                {
                    "type": "redeem",
                    "secret": "abcdefgh"
                },
                {
                    "type": "sell",
                    "product": 1,
                    "authorized_by": null
                },
                ...
            ]
        }
    """
    queryset = Transaction.objects.all().prefetch_related('positions')
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        try:
            response = self.perform_create(request.data)
            return Response(response, status=status.HTTP_201_CREATED)
        except ProcessException as e:
            return Response(e.data, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def perform_create(self, data):
        trans = Transaction()
        if 'cash_given' in data:
            trans.cash_given = round_decimal(data.get('cash_given', '0.00'))
        trans.save()

        position_feedback = []
        success = True

        for inppos in data.get('positions', []):
            postype = inppos.get('type', '')
            try:
                if postype == "redeem":
                    pos = redeem_preorder_ticket(**inppos)
                else:
                    raise FlowError('Type {} is not yet implemented'.format(postype))
            except FlowError as e:
                position_feedback.append({
                    'success': False,
                    'message': e.message,
                    'type': e.type,
                    'missing_field': e.missing_field
                })
                success = False
            else:
                position_feedback.append({
                    'success': True,
                })
                pos.transaction = trans
                pos.save()

        response = {
            'success': success,
            'positions': position_feedback
        }

        if success:
            return response
        else:
            # Break out of atomic transaction so everything gets rolled back!
            raise ProcessException(response)


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
