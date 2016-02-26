import random
import string
from datetime import timedelta
from decimal import Decimal

from c6sh.core.models import (
    ListConstraint, TimeConstraint, ListConstraintEntry, TransactionPosition,
    Preorder, Item, PreorderPosition, Transaction, Quota, Product, ProductItem,
    User, Cashdesk, CashdeskSession, CashdeskSessionItem, WarningConstraint
)
from django.utils.timezone import now
from faker import Factory


def user_factory(troubleshooter=False, superuser=False):
    fake = Factory.create('en-US')
    return User.objects.create(username=fake.user_name(),
                               password=fake.password(),
                               firstname=fake.first_name(),
                               lastname=fake.last_name(),
                               is_active=True,
                               is_superuser=superuser,
                               is_troubleshooter=troubleshooter)


def item_factory():
    fake = Factory.create('en-US')
    return Item.objects.create(name=fake.state(),
                               description=fake.bs(),
                               initial_stock=random.randint(50, 1000))


def cashdesk_factory(ip=None, active=None):
    fake = Factory.create('en-US')
    return Cashdesk.objects.create(name='Cashdesk {}'.format(random.randint(0, 10)),
                                   ip_address=ip or fake.ipv4(),
                                   is_active=active if active is not None else True)


def cashdesk_session_before_factory():
    fake = Factory.create('en-US')
    cd = CashdeskSession.objects.create(cashdesk=cashdesk_factory(),
                                        user=user_factory(),
                                        start=now() - timedelta(hours=2),
                                        cash_before=random.choice([50 * i for i in range(6)]),
                                        backoffice_user_before=user_factory(superuser=True))

    items = [item_factory() for _ in range(3)]
    for i in items:
        CashdeskSessionItem.objects.create(session=cd,
                                           item=i,
                                           amount_before=random.randint(1, i.initial_stock))
    return cd


def quota_factory(size=None):
    return Quota.objects.create(name='Day {} Quota'.format(random.randint(0, 4)),
                                size=random.randint(50, 300) if size is None else size)


def time_constraint_factory(active=True):
    fake = Factory.create('en-US')
    if active:
        start = fake.date_time_between(start='-23h', end='-1h')
        end = fake.date_time_between(start='+1h', end='+23h')
    else:
        start = fake.date_time_between(start='-23h', end='-10h')
        end = fake.date_time_between(start='-9h', end='-2h')
    return TimeConstraint.objects.create(name='Time Constraint',
                                         start=start,
                                         end=end)


def product_factory(items=False):
    fake = Factory.create('en-US')
    p = Product.objects.create(name=fake.catch_phrase(),
                               price=random.choice([50 * i for i in range(5)]),
                               tax_rate=19)
    if items:
        ProductItem.objects.create(item=item_factory(), product=p,
                                   amount=1)
    return p


def preorder_factory(paid=False):
    return Preorder.objects.create(order_code=''.join(random.choice(string.ascii_letters) for _ in range(24)),
                                   is_paid=paid)


def preorder_position_factory(paid=False, redeemed=False):
    pp = PreorderPosition.objects.create(preorder=preorder_factory(paid),
                                         secret=''.join(random.choice(string.ascii_letters) for _ in range(24)),
                                         product=product_factory())
    if redeemed:
        TransactionPosition.objects.create(
            type='redeem', preorder_position=pp,
            value=Decimal('0.00'), tax_rate=Decimal('0.00'), tax_value=Decimal('0.00'),
            product=product_factory(), transaction=transaction_factory()
        )
    return pp


def transaction_factory():
    return Transaction.objects.create(session=cashdesk_session_before_factory())


def transaction_position_factory(transaction=None, product=None):
    transaction = transaction or transaction_factory()
    product = product or product_factory(items=True)
    TransactionPosition.objects.create(
        type='sell', value=product.price, tax_rate=product.tax_rate,
        product=product, transaction=transaction
    )


def warning_constraint_factory():
    return WarningConstraint.objects.create(
        name='U18 warning',
        message='Please check that the person is younger than 18 years old.'
    )


def list_constraint_factory():
    return ListConstraint.objects.create(
        name='VIP members'
    )


def list_constraint_entry_factory(list_constraint, redeemed=False):
    fake = Factory.create('en-US')
    e = ListConstraintEntry.objects.create(
        list=list_constraint, name=fake.name(), identifier=str(random.randint(0, 100000))
    )
    if redeemed:
        TransactionPosition.objects.create(
            type='redeem', listentry=e,
            value=Decimal('0.00'), tax_rate=Decimal('0.00'), tax_value=Decimal('0.00'),
            product=product_factory(), transaction=transaction_factory()
        )
    return e
