from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.models import (
    Cashdesk, ListConstraint, ListConstraintEntry, Preorder, PreorderPosition,
    Product, Transaction,
)
from ..core.utils import round_decimal
from ..core.utils.flow import (
    FlowError, redeem_preorder_ticket, reverse_transaction, sell_ticket,
)
from .serializers import (
    ListConstraintEntrySerializer, ListConstraintSerializer,
    PreorderPositionSerializer, PreorderSerializer, ProductSerializer,
    TransactionSerializer,
)


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

    def get_queryset(self):
        queryset = PreorderPosition.objects.all()
        exact_param = self.request.GET.get('secret', None)
        search_param = self.request.GET.get('search', None)
        if exact_param is not None:
            queryset = queryset.filter(secret__iexact=exact_param)
        elif search_param is not None and len(search_param) >= 6:
            queryset = queryset.filter(secret__istartswith=search_param)
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
            response = self.perform_create(request)
            return Response(response, status=status.HTTP_201_CREATED)
        except ProcessException as e:
            return Response(e.data, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def perform_create(self, request):
        data = request.data
        trans = Transaction()
        if 'cash_given' in data:
            trans.cash_given = round_decimal(data.get('cash_given', '0.00'))
        session = self.request.user.get_current_session()
        if not session:  # noqa
            raise RuntimeError('This should never happen because the auth layer should handle this.')
        trans.session = session
        trans.save()

        position_feedback = []
        success = True
        pos = data.get('positions', [])

        if not pos:
            raise ProcessException('Empty transaction')

        for inppos in pos:
            postype = inppos.get('type', '')
            try:
                if postype == "redeem":
                    pos = redeem_preorder_ticket(**inppos)
                elif postype == "sell":
                    pos = sell_ticket(**inppos)
                else:  # noqa
                    raise FlowError('Type {} is not yet implemented'.format(postype))
            except FlowError as e:
                position_feedback.append({
                    'success': False,
                    'message': e.message,
                    'type': e.type,
                    'missing_field': e.missing_field,
                    'bypass_price': e.bypass_price
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
            trans.print_receipt(do_open_drawer=True)
            response['id'] = trans.pk
            return response
        else:
            # Break out of atomic transaction so everything gets rolled back!
            raise ProcessException(response)

    @detail_route(methods=["POST"])
    def reverse(self, *args, **kwargs):
        session = self.request.user.get_current_session()
        if not session:  # noqa
            raise RuntimeError('This should never happen because the auth layer should handle this.')
        try:
            new_id = reverse_transaction(kwargs.get('pk'), session)
            Transaction.objects.get(pk=new_id).print_receipt(do_open_drawer=False)
            return Response({
                'success': True,
                'id': new_id
            }, status=status.HTTP_201_CREATED)
        except FlowError as e:
            return Response({
                'success': False,
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(ReadOnlyModelViewSet):

    queryset = Product.objects.prefetch_related('product_items', 'product_items__item').all()
    serializer_class = ProductSerializer


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
                queryset = queryset.filter(Q(name__contains=search_param) | Q(identifier__contains=search_param))
            else:
                queryset = queryset.none()
        else:
            queryset = queryset.none()
        return queryset


class CashdeskActionViewSet(ReadOnlyModelViewSet):
    """ Hacky class to use restframework capabilities without being RESTful.
    We don't expose a queryset, and use a random serializer.\n\n
    Allowed actions: open-drawer and reprint-receipt
    """
    serializer_class = ListConstraintEntrySerializer
    queryset = Cashdesk.objects.none()

    @list_route(methods=["POST"], url_path='open-drawer')
    def open_drawer(self, request):
        session = request.user.get_current_session()
        if not session:  # noqa
            raise RuntimeError('This should never happen because the auth layer should handle this.')
        session.cashdesk.printer.open_drawer()
        return Response({'success': True})

    @list_route(methods=["POST"], url_path='reprint-receipt')
    def reprint_receipt(self, request):
        session = request.user.get_current_session()
        if not session:  # noqa
            raise RuntimeError('This should never happen because the auth layer should handle this.')

        try:
            transaction = Transaction.objects.get(pk=request.data.get('transaction'))
            session.cashdesk.printer.print_receipt(transaction, do_open_drawer=False)
            return Response({'success': True})
        except Transaction.DoesNotExist:
            return Response({'success': False, 'error': 'Transaction not found.'}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=["POST"], url_path='request-resupply')
    def request_resupply(self, request):
        session = request.user.get_current_session()
        if not session:  # noqa
            raise RuntimeError('This should never happen because the auth layer should handle this.')

        session.request_resupply()
        return Response({'success': True})
