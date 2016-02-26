from decimal import Decimal

import pytest
from c6sh.core.models import TransactionPosition
from ...factories import (
    transaction_position_factory, product_factory, time_constraint_factory,
    quota_factory, transaction_factory
)


@pytest.mark.django_db
def test_transactionposition_was_reversed():
    tp = transaction_position_factory()
    assert not tp.was_reversed()
    tp2 = transaction_position_factory()
    tp2.type = 'reverse'
    tp2.reverses = tp
    tp2.save()
    assert tp.was_reversed()
    assert not tp2.was_reversed()


@pytest.mark.django_db
def test_product_available_simple():
    p = product_factory()
    assert p.is_available()


@pytest.mark.django_db
def test_product_available_timeframe():
    p = product_factory()
    t = time_constraint_factory(active=True)
    t.products.add(p)
    assert p.is_available()


@pytest.mark.django_db
def test_product_unavailable_timeframe():
    p = product_factory()
    t = time_constraint_factory(active=False)
    t.products.add(p)
    assert not p.is_available()


@pytest.mark.django_db
def test_product_available_quota():
    p = product_factory()
    q = quota_factory(size=20)
    q.products.add(p)
    assert p.is_available()


@pytest.mark.django_db
def test_product_unavailable_quota():
    p = product_factory()
    q = quota_factory(size=0)
    q.products.add(p)
    assert not p.is_available()


@pytest.mark.django_db
def test_tax_calculation():
    trans = transaction_factory()
    pos = TransactionPosition(type='sale', tax_rate=Decimal('7.00'), value=Decimal('1.07'),
                              transaction=trans, product=product_factory())
    pos.save()
    assert pos.tax_value == Decimal('0.07')


@pytest.mark.django_db
def test_tax_calculation_no_tax():
    trans = transaction_factory()
    pos = TransactionPosition(type='sale', tax_rate=Decimal('0.00'), value=Decimal('1.19'),
                              transaction=trans, product=product_factory())
    pos.save()
    assert pos.tax_value == Decimal('0.00')


@pytest.mark.django_db
def test_sale_copy_tax_rate():
    trans = transaction_factory()
    pos = TransactionPosition(type='sale', transaction=trans, product=product_factory())
    pos.save()
    assert pos.value == pos.product.price
    assert pos.tax_rate == pos.product.tax_rate


@pytest.mark.django_db
def test_sale_copy_items():
    trans = transaction_factory()
    prod = product_factory(items=True)
    assert prod.items.exists()
    pos = TransactionPosition(type='sale', transaction=trans, product=prod)
    pos.save()
    assert set(pos.items.all()) == set(prod.items.all())
