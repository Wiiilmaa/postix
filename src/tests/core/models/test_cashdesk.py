from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils.timezone import now
from tests.factories import (
    cashdesk_session_before_factory, transaction_factory,
    transaction_position_factory, user_factory,
)

from c6sh.core.models import (
    Item, ItemMovement, Product, ProductItem, TransactionPosition,
)
from c6sh.core.utils.flow import reverse_transaction


@pytest.mark.django_db
def test_session_active():
    session = cashdesk_session_before_factory()
    assert session.is_active()


@pytest.mark.django_db
def test_session_not_active():
    session = cashdesk_session_before_factory()
    session.end = now() - timedelta(hours=1)
    assert not session.is_active()


@pytest.mark.django_db
def test_current_items():
    session = cashdesk_session_before_factory(create_items=False)
    buser = user_factory(troubleshooter=True, superuser=True)
    item_full = Item.objects.create(name='Full pass', description='', initial_stock=200)
    item_1d = Item.objects.create(name='One day pass', description='', initial_stock=100)
    prod_full = Product.objects.create(name='Full ticket', price=23, tax_rate=19)
    prod_1d = Product.objects.create(name='One day ticket', price=12, tax_rate=19)
    ProductItem.objects.create(product=prod_full, item=item_full, amount=1)
    ProductItem.objects.create(product=prod_1d, item=item_1d, amount=1)
    ItemMovement.objects.create(session=session, item=item_full, amount=20, backoffice_user=buser)
    ItemMovement.objects.create(session=session, item=item_1d, amount=10, backoffice_user=buser)

    for i in range(3):
        transaction_position_factory(transaction_factory(session), prod_full)
    for i in range(2):
        transaction_position_factory(transaction_factory(session), prod_1d)

    trans = transaction_position_factory(transaction_factory(session), prod_1d).transaction
    reverse_transaction(trans_id=trans.pk, current_session=session)

    session.end = now()
    session.save()
    ItemMovement.objects.create(session=session, item=item_full, amount=-17, backoffice_user=buser)
    ItemMovement.objects.create(session=session, item=item_1d, amount=-5, backoffice_user=buser)

    assert session.get_current_items() == [
        {
            'movements': 20,
            'total': 0,
            'transactions': 3,
            'item': item_full,
            'final_movements': 17
        },
        {
            'movements': 10,
            'total': 3,
            'transactions': 2,
            'item': item_1d,
            'final_movements': 5
        }
    ]


@pytest.mark.django_db
def test_cash_transaction_total():
    session = cashdesk_session_before_factory(create_items=False)
    prod_full = Product.objects.create(name='Full ticket', price=23, tax_rate=19)

    for i in range(3):
        transaction_position_factory(transaction_factory(session), prod_full)
    trans = transaction_position_factory(transaction_factory(session), prod_full).transaction
    reverse_transaction(trans_id=trans.pk, current_session=session)

    TransactionPosition.objects.create(
        type='redeem', value=10, tax_rate=19, product=prod_full, transaction=transaction_factory(session),
        has_constraint_bypass=True
    )

    assert session.get_cash_transaction_total() == 23 * 3 + 10


@pytest.mark.django_db
@pytest.mark.xfail(reason="This needs some discussion.")
def test_product_sales():
    session = cashdesk_session_before_factory(create_items=False)
    prod_full = Product.objects.create(name='Full ticket', price=23, tax_rate=19)

    for i in range(3):
        transaction_position_factory(transaction_factory(session), prod_full)
    trans = transaction_position_factory(transaction_factory(session), prod_full)
    reverse_transaction(trans_id=trans.pk, current_session=session)

    TransactionPosition.objects.create(
        type='redeem', value=10, tax_rate=19, product=prod_full, transaction=transaction_factory(session),
        has_constraint_bypass=True
    )

    assert session.get_product_sales() == [
        {
            'presales': 1,
            'value_single': False,  #  Decimal('23.00'),  # What should this be?
            'product': prod_full,
            'value_total': Decimal('79.00'),
            'reversals': 1,
            'sales': 4
        }
    ]
