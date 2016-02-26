from decimal import Decimal

import pytest
from c6sh.core.models import WarningConstraintProduct, ListConstraintProduct, PreorderPosition, TransactionPosition
from c6sh.core.utils.checks import is_redeemed
from c6sh.core.utils.flow import redeem_preorder_ticket, FlowError
from tests.factories import (
    preorder_position_factory, warning_constraint_factory, list_constraint_factory,
    list_constraint_entry_factory, user_factory,
    transaction_factory)


@pytest.mark.django_db
def test_invalid():
    with pytest.raises(FlowError) as excinfo:
        redeem_preorder_ticket(secret='abcde')
    assert excinfo.value.message == 'No ticket found with the given secret.'

@pytest.mark.django_db
def test_unpaid():
    with pytest.raises(FlowError) as excinfo:
        redeem_preorder_ticket(secret=preorder_position_factory().secret)
    assert excinfo.value.message == 'Ticket has not been paid for.'


@pytest.mark.django_db
def test_already_redeemed():
    with pytest.raises(FlowError) as excinfo:
        redeem_preorder_ticket(secret=preorder_position_factory(paid=True, redeemed=True).secret)
    assert excinfo.value.message == 'Ticket has already been redeemed.'


@pytest.mark.django_db
def test_simple_valid():
    pp = preorder_position_factory(paid=True, redeemed=False)
    pos = redeem_preorder_ticket(secret=pp.secret)
    assert isinstance(pos, TransactionPosition)
    assert pos.value == Decimal('0.00')
    assert pos.product == pp.product
    pos.transaction = transaction_factory()
    pos.save()
    assert is_redeemed(pp)


@pytest.mark.django_db
def test_preorder_warning():
    pp = preorder_position_factory(paid=True)
    pp.preorder.warning_text = "Foo"
    pp.preorder.save()
    with pytest.raises(FlowError) as excinfo:
        redeem_preorder_ticket(secret=pp.secret)
    assert excinfo.value.message == 'Foo'
    assert excinfo.value.type == 'confirmation'
    assert excinfo.value.missing_field == 'warning_acknowledged'


@pytest.mark.django_db
def test_preorder_warning_constraint():
    pp = preorder_position_factory(paid=True)
    warning_constraint = warning_constraint_factory()
    WarningConstraintProduct.objects.create(
        product=pp.product, constraint=warning_constraint
    )
    with pytest.raises(FlowError) as excinfo:
        redeem_preorder_ticket(secret=pp.secret)
    assert excinfo.value.message == warning_constraint.message
    assert excinfo.value.type == 'confirmation'
    assert excinfo.value.missing_field == 'warning_{}_acknowledged'.format(warning_constraint.pk)


@pytest.mark.django_db
def test_preorder_warning_constraint_passed():
    pp = preorder_position_factory(paid=True)
    warning_constraint = warning_constraint_factory()
    WarningConstraintProduct.objects.create(
        product=pp.product, constraint=warning_constraint
    )
    options = {
        'warning_{}_acknowledged'.format(warning_constraint.pk): 'ok'
    }
    redeem_preorder_ticket(secret=pp.secret, **options)


@pytest.mark.django_db
def test_preorder_list_constraint():
    pp = preorder_position_factory(paid=True)
    list_constraint = list_constraint_factory()
    ListConstraintProduct.objects.create(
        product=pp.product, constraint=list_constraint
    )
    with pytest.raises(FlowError) as excinfo:
        redeem_preorder_ticket(secret=pp.secret)
    assert excinfo.value.message == 'This ticket can only redeemed by persons on the list "{}".'.format(
        list_constraint.name)
    assert excinfo.value.type == 'input'
    assert excinfo.value.missing_field == 'list_{}'.format(list_constraint.pk)


@pytest.mark.django_db
def test_preorder_list_constraint_unknown():
    pp = preorder_position_factory(paid=True)
    list_constraint = list_constraint_factory()
    ListConstraintProduct.objects.create(
        product=pp.product, constraint=list_constraint,
    )
    options = {
        'list_{}'.format(list_constraint.pk): '2'
    }
    with pytest.raises(FlowError) as excinfo:
        redeem_preorder_ticket(secret=pp.secret, **options)
    assert excinfo.value.message == 'Entry not found on list "{}".'.format(
        list_constraint.name)
    assert excinfo.value.type == 'input'
    assert excinfo.value.missing_field == 'list_{}'.format(list_constraint.pk)


@pytest.mark.django_db
def test_preorder_list_constraint_used():
    pp = preorder_position_factory(paid=True)
    list_constraint = list_constraint_factory()
    entry = list_constraint_entry_factory(list_constraint=list_constraint, redeemed=True)
    ListConstraintProduct.objects.create(
        product=pp.product, constraint=entry.list,
    )
    options = {
        'list_{}'.format(entry.list.pk): str(entry.id)
    }
    with pytest.raises(FlowError) as excinfo:
        redeem_preorder_ticket(secret=pp.secret, **options)
    assert excinfo.value.message == 'This list entry already has been used.'
    assert excinfo.value.type == 'input'
    assert excinfo.value.missing_field == 'list_{}'.format(list_constraint.pk)


@pytest.mark.django_db
def test_preorder_list_constraint_success():
    pp = preorder_position_factory(paid=True)
    list_constraint = list_constraint_factory()
    entry = list_constraint_entry_factory(list_constraint=list_constraint, redeemed=False)
    ListConstraintProduct.objects.create(
        product=pp.product, constraint=entry.list,
    )
    options = {
        'list_{}'.format(entry.list.pk): str(entry.id)
    }
    pos = redeem_preorder_ticket(secret=pp.secret, **options)
    assert pos.listentry == entry


@pytest.mark.django_db
def test_preorder_list_constraint_troubleshooter_bypass():
    pp = preorder_position_factory(paid=True)
    list_constraint = list_constraint_factory()
    ListConstraintProduct.objects.create(
        product=pp.product, constraint=list_constraint,
    )
    user = user_factory(troubleshooter=True)
    user.auth_token = 'abcdefg'
    user.save()
    options = {
        'list_{}'.format(list_constraint.pk): str(user.auth_token)
    }
    pos = redeem_preorder_ticket(secret=pp.secret, **options)
    assert pos.listentry is None
    assert pos.authorized_by == user
