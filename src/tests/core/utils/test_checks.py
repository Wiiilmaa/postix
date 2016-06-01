from decimal import Decimal

import pytest

from c6sh.core.models import TransactionPosition
from c6sh.core.utils.checks import is_redeemed

from ...factories import (
    list_constraint_entry_factory, list_constraint_factory,
    preorder_position_factory, product_factory, transaction_factory,
)


@pytest.mark.django_db
def test_redeemed_entry():
    list_constraint = list_constraint_factory()
    entry = list_constraint_entry_factory(list_constraint, redeemed=True)
    assert is_redeemed(entry)


@pytest.mark.django_db
def test_unredeemed_entry():
    list_constraint = list_constraint_factory()
    entry = list_constraint_entry_factory(list_constraint, redeemed=False)
    assert not is_redeemed(entry)


@pytest.mark.django_db
def test_reversed_entry():
    list_constraint = list_constraint_factory()
    entry = list_constraint_entry_factory(list_constraint, redeemed=True)
    TransactionPosition.objects.create(
        type='reverse', listentry=entry,
        value=Decimal('0.00'), tax_rate=Decimal('0.00'), tax_value=Decimal('0.00'),
        product=product_factory(), transaction=transaction_factory()
    )
    assert not is_redeemed(entry)


@pytest.mark.django_db
def test_redeemed_preorder():
    pp = preorder_position_factory(paid=True, redeemed=True)
    assert is_redeemed(pp)


@pytest.mark.django_db
def test_unredeemed_preorder():
    pp = preorder_position_factory(paid=True, redeemed=False)
    assert not is_redeemed(pp)


@pytest.mark.django_db
def test_reversed_preorder():
    pp = preorder_position_factory(paid=True, redeemed=True)
    TransactionPosition.objects.create(
        type='reverse', preorder_position=pp,
        value=Decimal('0.00'), tax_rate=Decimal('0.00'), tax_value=Decimal('0.00'),
        product=product_factory(), transaction=transaction_factory()
    )
    assert not is_redeemed(pp)
