from decimal import Decimal

from .checks import is_redeemed
from ..models import PreorderPosition, ListConstraintEntry, TransactionPosition, User, ListConstraintProduct


class FlowError(Exception):
    def __init__(self, msg, type="error", missing_field=None):
        self.message = msg
        self.type = type
        self.missing_field = missing_field

    def __str__(self):
        return self.message


def redeem_preorder_ticket(**kwargs):
    pos = TransactionPosition()

    if 'secret' not in kwargs:
        raise FlowError('No secret has been given.')

    try:
        pp = PreorderPosition.objects.get(secret=kwargs.get('secret'))
    except PreorderPosition.DoesNotExist:
        raise FlowError('No ticket found with the given secret.')

    if not pp.preorder.is_paid:
        raise FlowError('Ticket has not been paid for.')

    if is_redeemed(pp):
        raise FlowError('Ticket has already been redeemed.')

    if pp.preorder.warning_text and 'warning_acknowledged' not in kwargs:
        raise FlowError(pp.preorder.warning_text, type='confirmation',
                        missing_field='warning_acknowledged')

    for c in pp.product.product_warning_contraints.all():
        if 'warning_{}_acknowledged'.format(c.constraint.pk) not in kwargs:
            raise FlowError(c.constraint.message, type='confirmation',
                            missing_field='warning_{}_acknowledged'.format(c.pk))

    try:
        c = pp.product.product_list_constraint
        entryid = kwargs.get('list_{}'.format(c.constraint.pk), None)
        if not entryid:
            raise FlowError('This ticket can only redeemed by persons on the list "{}".'.format(
                c.constraint.name), type='input', missing_field='name_{}'.format(c.constraint.pk))
        try:
            entry = c.constraint.entries.get(id=entryid)
            if is_redeemed(entry):
                raise FlowError('This list entry has already been used.'.format(c.constraint.name),
                                type='input', missing_field='name_{}'.format(c.constraint.pk))
            else:
                pos.listentry = entry
        except ListConstraintEntry.DoesNotExist:
            try:
                pos.authorized_by = User.objects.get(is_troubleshooter=True, auth_token=entryid)
            except User.DoesNotExist:
                raise FlowError('Entry not found on list "{}".'.format(c.constraint.name),
                                type='input', missing_field='name_{}'.format(c.constraint.pk))
    except ListConstraintProduct.DoesNotExist:
        pass

    # TODO: Handle upgrades
    pos.product = pp.product
    pos.value = pos.tax_rate = pos.tax_value = Decimal('0.00')
    return pos
