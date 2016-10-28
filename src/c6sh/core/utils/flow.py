import copy
from decimal import Decimal

from c6sh.core.models import Product

from ..models import (
    CashdeskSession, ListConstraintEntry, ListConstraintProduct,
    PreorderPosition, Transaction, TransactionPosition,
    TransactionPositionItem, User,
)
from .checks import is_redeemed


class FlowError(Exception):
    def __init__(self, msg, type="error", missing_field=None, bypass_price=None):
        self.message = msg
        self.type = type
        self.missing_field = missing_field
        self.bypass_price = bypass_price

    def __str__(self):
        return self.message


def redeem_preorder_ticket(**kwargs):
    """
    Creates a TransactionPosition object that validates a given preorder position.
    This checks the various constraints placed on the given position and item and
    raises a FlowError if one of the conditions can't be met. This FlowError will
    contain information which additional keyword arguments you need to provide to
    fulfull the conditions (if possible).

    :param secret: The secret of the preorder position (i.e. the scanned barcode)
    :returns: The TransactionPosition object
    """
    pos = TransactionPosition(type='redeem')
    bypass_price = bypass_price_paying = Decimal(kwargs.get('bypass_price', '0.00'))
    bypass_taxrate = None

    if 'secret' not in kwargs:  # noqa
        raise FlowError('No secret has been given.')

    try:
        pp = PreorderPosition.objects.select_for_update().get(secret=kwargs.get('secret'))
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
            if c.price is not None and bypass_price_paying >= c.price:
                bypass_price_paying -= c.price
                bypass_taxrate = c.tax_rate
            else:
                raise FlowError(c.constraint.message, type='confirmation',
                                missing_field='warning_{}_acknowledged'.format(c.constraint.pk),
                                bypass_price=c.price)

    try:
        c = pp.product.product_list_constraint
        entryid = kwargs.get('list_{}'.format(c.constraint.pk), None)
        if c.price is not None and bypass_price_paying >= c.price:
            bypass_price_paying -= c.price
            if bypass_taxrate is not None and bypass_taxrate != c.tax_rate:
                raise FlowError("Multiple upgrades with different taxrates are not supported.")
            bypass_taxrate = c.tax_rate
        else:
            if not entryid:
                raise FlowError(
                    'This ticket can only redeemed by persons on the list "{}".'.format(c.constraint.name),
                    type='input', missing_field='list_{}'.format(c.constraint.pk), bypass_price=c.price)
            try:
                pos.authorized_by = User.objects.get(is_troubleshooter=True, auth_token=entryid)
            except User.DoesNotExist:  # noqa
                try:
                    entry = c.constraint.entries.get(identifier=entryid)
                    if is_redeemed(entry):
                        raise FlowError('This list entry already has been used.'.format(c.constraint.name),
                                        type='input', missing_field='list_{}'.format(c.constraint.pk),
                                        bypass_price=c.price)
                    else:
                        pos.listentry = entry
                except ListConstraintEntry.DoesNotExist:
                    raise FlowError('Entry not found on list "{}".'.format(c.constraint.name),
                                    type='input', missing_field='list_{}'.format(c.constraint.pk),
                                    bypass_price=c.price)

    except ListConstraintProduct.DoesNotExist:
        pass

    pos.product = pp.product
    pos.preorder_position = pp
    if bypass_taxrate is not None and bypass_price:
        pos.value = bypass_price
        pos.tax_rate = bypass_taxrate  # tax_value is calculated by .save()
    else:
        pos.value = pos.tax_rate = Decimal('0.00')
    return pos


def sell_ticket(**kwargs):
    """
    Creates a TransactionPosition object that sells a given product.
    This checks the various constraints placed on the given product and item and
    raises a FlowError if one of the conditions can't be met. This FlowError will
    contain information which additional keyword arguments you need to provide to
    fulfull the conditions (if possible).

    :param product: The ID of the product to sell.
    :returns: The TransactionPosition object
    """
    pos = TransactionPosition(type='sell')

    if 'product' not in kwargs:  # noqa
        raise FlowError('No product given.')

    try:
        product = Product.objects.get(id=kwargs.get('product'))
    except Product.DoesNotExist:
        raise FlowError('Product ID not known.')

    if not product.is_available():
        raise FlowError('Product currently unavailable or sold out.')

    if product.requires_authorization:
        auth = kwargs.get('auth', '!invalid')
        try:
            pos.authorized_by = User.objects.get(is_troubleshooter=True, auth_token=auth)
        except User.DoesNotExist:  # noqa
            raise FlowError('This sale requires authorization by a troubleshooter.',
                            type='input', missing_field='auth')

    for c in product.product_warning_constraints.all():
        if 'warning_{}_acknowledged'.format(c.constraint.pk) not in kwargs:
            raise FlowError(c.constraint.message, type='confirmation',
                            missing_field='warning_{}_acknowledged'.format(c.constraint.pk))

    try:
        c = product.product_list_constraint
        entryid = kwargs.get('list_{}'.format(c.constraint.pk), None)
        if not entryid:
            raise FlowError(
                'This ticket can only redeemed by persons on the list "{}".'.format(c.constraint.name),
                type='input', missing_field='list_{}'.format(c.constraint.pk))
        if not entryid.isdigit():
            try:
                pos.authorized_by = User.objects.get(is_troubleshooter=True, auth_token=entryid)
            except User.DoesNotExist:  # noqa
                raise FlowError('Please supply a list entry ID.',
                                type='input', missing_field='list_{}'.format(c.constraint.pk))
        else:
            try:
                entry = c.constraint.entries.get(identifier=entryid)
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


def reverse_transaction(trans_id: int, current_session: CashdeskSession, authorized_by=None):
    """
    Creates a Transaction that reverses an earlier transaction as a whole.

    :param trans_id: The ID of the transaction to reverse
    :returns: The new Transaction object
    """
    try:
        old_transaction = Transaction.objects.get(id=trans_id)
    except Transaction.DoesNotExist:
        raise FlowError('Transaction ID not known.')

    if not current_session.is_active():  # noqa (caught by auth layer)
        raise FlowError('You need to provide an active session.')

    if old_transaction.session != current_session:
        if not current_session.user.is_troubleshooter:
            if not authorized_by or not authorized_by.is_troubleshooter:
                raise FlowError('Only troubleshooters can reverse sales from other sessions.')

    if old_transaction.has_reversed_positions:
        raise FlowError('At least one position of this transaction already has been reversed.')
    if old_transaction.has_reversals:
        raise FlowError('At least one position of this transaction is a reversal.')

    new_transaction = Transaction.objects.create(session=current_session)
    for old_pos in old_transaction.positions.all():
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

    return new_transaction.pk


def reverse_transaction_position(trans_pos_id, current_session: CashdeskSession, authorized_by=None):
    """
    Creates a Transaction that reverses a single transaction position.

    :param trans_pos_id: The ID of the transaction position to reverse
    :returns: The new Transaction object
    """
    try:
        old_pos = TransactionPosition.objects.get(id=trans_pos_id)
    except TransactionPosition.DoesNotExist:
        raise FlowError('TransactionPosition ID not known.')

    if not current_session.is_active():  # noqa (caught by auth layer)
        raise FlowError('You need to provide an active session.')

    if old_pos.transaction.session != current_session:
        if not current_session.user.is_troubleshooter:
            if not authorized_by or not authorized_by.is_troubleshooter:
                raise FlowError('Only troubleshooters can reverse sales from other sessions.')

    if old_pos.reversed_by.exists():
        raise FlowError('This position already has been reversed.')
    if old_pos.type == 'reverse':
        raise FlowError('This position already is a reversal.')

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

    return new_transaction.pk
