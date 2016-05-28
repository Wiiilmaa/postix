import copy
from decimal import Decimal

from c6sh.core.models import Product
from .checks import is_redeemed
from ..models import (
    PreorderPosition, ListConstraintEntry, TransactionPosition, User, ListConstraintProduct, Transaction,
    CashdeskSession, TransactionPositionItem
)


class FlowError(Exception):
    def __init__(self, msg, type="error", missing_field=None):
        self.message = msg
        self.type = type
        self.missing_field = missing_field

    def __str__(self):
        return self.message


def redeem_preorder_ticket(**kwargs):
    pos = TransactionPosition(type='redeem')

    if 'secret' not in kwargs:  # noqa
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

    for c in pp.product.product_warning_constraints.all():
        if 'warning_{}_acknowledged'.format(c.constraint.pk) not in kwargs:
            raise FlowError(c.constraint.message, type='confirmation',
                            missing_field='warning_{}_acknowledged'.format(c.pk))

    try:
        c = pp.product.product_list_constraint
        entryid = kwargs.get('list_{}'.format(c.constraint.pk), None)
        if not entryid:
            raise FlowError('This ticket can only redeemed by persons on the list "{}".'.format(
                c.constraint.name), type='input', missing_field='list_{}'.format(c.constraint.pk))
        if not entryid.isdigit():
            try:
                # TODO: This breaks numeric-only auth_tokens. Either we make this logic more
                # complicated or we enforce characters in auth_tokens.
                pos.authorized_by = User.objects.get(is_troubleshooter=True, auth_token=entryid)
            except User.DoesNotExist:  # noqa
                raise FlowError('Please supply a list entry ID.',
                                type='input', missing_field='list_{}'.format(c.constraint.pk))
        else:
            try:
                entry = c.constraint.entries.get(id=entryid)
                if is_redeemed(entry):
                    raise FlowError('This list entry already has been used.'.format(c.constraint.name),
                                    type='input', missing_field='list_{}'.format(c.constraint.pk))
                else:
                    pos.listentry = entry
            except ListConstraintEntry.DoesNotExist:
                raise FlowError('Entry not found on list "{}".'.format(c.constraint.name),
                                type='input', missing_field='list_{}'.format(c.constraint.pk))
    except ListConstraintProduct.DoesNotExist:
        pass

    # TODO: Handle upgrades
    pos.product = pp.product
    pos.preorder_position = pp
    pos.value = pos.tax_rate = pos.tax_value = Decimal('0.00')
    return pos


def sell_ticket(**kwargs):
    pos = TransactionPosition(type='sell')

    if 'product' not in kwargs:  # noqa
        raise FlowError('No product given.')

    try:
        product = Product.objects.get(id=kwargs.get('product'))
    except Product.DoesNotExist:
        raise FlowError('Product ID not known.')

    if not product.is_available():
        raise FlowError('Product currently unavailable or sold out.')

    for c in product.product_warning_constraints.all():
        if 'warning_{}_acknowledged'.format(c.constraint.pk) not in kwargs:
            raise FlowError(c.constraint.message, type='confirmation',
                            missing_field='warning_{}_acknowledged'.format(c.pk))

    try:
        c = product.product_list_constraint
        entryid = kwargs.get('list_{}'.format(c.constraint.pk), None)
        if not entryid:
            raise FlowError('This ticket can only redeemed by persons on the list "{}".'.format(
                c.constraint.name), type='input', missing_field='list_{}'.format(c.constraint.pk))
        if not entryid.isdigit():
            try:
                # TODO: This breaks numeric-only auth_tokens. Either we make this logic more
                # complicated or we enforce characters in auth_tokens.
                pos.authorized_by = User.objects.get(is_troubleshooter=True, auth_token=entryid)
            except User.DoesNotExist:  # noqa
                raise FlowError('Please supply a list entry ID.',
                                type='input', missing_field='list_{}'.format(c.constraint.pk))
        else:
            try:
                entry = c.constraint.entries.get(id=entryid)
                if is_redeemed(entry):
                    raise FlowError('This list entry already has been used.'.format(c.constraint.name),
                                    type='input', missing_field='list_{}'.format(c.constraint.pk))
                else:
                    pos.listentry = entry
            except ListConstraintEntry.DoesNotExist:
                raise FlowError('Entry not found on list "{}".'.format(c.constraint.name),
                                type='input', missing_field='list_{}'.format(c.constraint.pk))
    except ListConstraintProduct.DoesNotExist:
        pass

    pos.product = product  # value, tax_* and items will be set automatically on save()
    return pos


def reverse_transaction(trans_id, current_session: CashdeskSession):
    try:
        old_transaction = Transaction.objects.get(id=trans_id)
    except Transaction.DoesNotExist:
        raise FlowError('Transaction ID not known.')

    if not current_session.is_active():  # noqa (catched by auth layer)
        raise FlowError('You need to provide an active session.')

    if old_transaction.session != current_session:
        if not current_session.user.is_troubleshooter:
            raise FlowError('Only troubleshooters can reverse sales from other sessions.')

    new_transaction = Transaction.objects.create(session=current_session)
    for old_pos in old_transaction.positions.all():
        if old_pos.reversed_by.exists():
            raise FlowError('At least one position of this transaction already has been reversed.')
        new_pos = copy.copy(old_pos)
        new_pos.transaction = new_transaction
        new_pos.pk = None
        new_pos.type = 'reverse'
        new_pos.value *= -1
        new_pos.tax_value *= -1
        new_pos.reverses = old_pos
        new_pos.authorized_by = None
        new_pos.save()
        for ip in TransactionPositionItem.objects.filter(position=new_pos):
            ip.amount *= -1
            ip.save()

    return new_transaction


def reverse_transaction_position(trans_pos_id, current_session: CashdeskSession):
    try:
        old_pos = TransactionPosition.objects.get(id=trans_pos_id)
    except TransactionPosition.DoesNotExist:
        raise FlowError('TransactionPosition ID not known.')

    if not current_session.is_active():  # noqa (catched by auth layer)
        raise FlowError('You need to provide an active session.')

    if old_pos.transaction.session != current_session:
        if not current_session.user.is_troubleshooter:
            raise FlowError('Only troubleshooters can reverse sales from other sessions.')

    if old_pos.reversed_by.exists():
        raise FlowError('This position already has been reversed.')

    new_transaction = Transaction(session=current_session)
    new_transaction.save()
    new_pos = copy.copy(old_pos)
    new_pos.transaction = new_transaction
    new_pos.pk = None
    new_pos.type = 'reverse'
    new_pos.value *= -1
    new_pos.tax_value *= -1
    new_pos.reverses = old_pos
    new_pos.authorized_by = None
    new_pos.save()
    for ip in TransactionPositionItem.objects.filter(position=new_pos):
        ip.amount *= -1
        ip.save()

    return new_transaction
