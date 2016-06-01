import pytest
from tests.factories import (
    product_factory, quota_factory, transaction_position_factory,
)


@pytest.mark.django_db
def test_quota_empty():
    quota = quota_factory(size=2)
    product = product_factory()
    quota.products.add(product)
    assert quota.is_available()


@pytest.mark.django_db
def test_quota_half_used():
    quota = quota_factory(size=4)
    product = product_factory()
    quota.products.add(product)
    [transaction_position_factory(product=product) for _ in range(2)]
    assert quota.is_available()


@pytest.mark.django_db
def test_quota_used():
    quota = quota_factory(size=4)
    product = product_factory()
    quota.products.add(product)
    [transaction_position_factory(product=product) for _ in range(5)]
    assert not quota.is_available()


@pytest.mark.django_db
def test_quota_used_multiple_products():
    quota = quota_factory(size=4)
    product1 = product_factory()
    quota.products.add(product1)
    product2 = product_factory()
    quota.products.add(product2)
    [transaction_position_factory(product=product1) for _ in range(2)]
    [transaction_position_factory(product=product2) for _ in range(2)]
    assert not quota.is_available()
