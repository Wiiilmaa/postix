import random
import string
from datetime import timedelta
from decimal import Decimal

from django.utils.crypto import get_random_string
from django.utils.timezone import now
from faker import Faker

from postix.core.models import (
    Cashdesk, CashdeskSession, Item, ItemMovement, ListConstraint,
    ListConstraintEntry, ListConstraintProduct, Preorder, PreorderPosition,
    Product, ProductItem, Quota, TimeConstraint, Transaction,
    TransactionPosition, User, WarningConstraint,
)


def user_factory(troubleshooter=False, superuser=False, backoffice=False, password=None):
    fake = Faker('en-US')
    u = User(username=fake.user_name(),
             firstname=fake.first_name(),
             lastname=fake.last_name(),
             is_active=True,
             is_superuser=superuser,
             is_backoffice_user=backoffice,
             is_troubleshooter=troubleshooter)
    u.set_password(password or fake.password())
    if troubleshooter:
        u.auth_token = get_random_string(32)
    u.save()
    return u


def item_factory():
    fake = Faker('en-US')
    return Item.objects.create(name=fake.state(),
                               description=fake.bs(),
                               initial_stock=random.randint(50, 1000))


def cashdesk_factory(ip=None, active=None):
    fake = Faker('en-US')
    return Cashdesk.objects.create(name='Cashdesk {}'.format(random.randint(0, 10)),
                                   ip_address=ip or fake.ipv4(),
                                   is_active=active if active is not None else True)


def cashdesk_session_before_factory(ip=None, user=None, create_items=True):
    cd = CashdeskSession.objects.create(cashdesk=cashdesk_factory(ip=ip),
                                        user=user or user_factory(),
                                        start=now() - timedelta(hours=2),
                                        cash_before=random.choice([50 * i for i in range(6)]),
                                        backoffice_user_before=user_factory(superuser=True))

    if create_items:
        items = [item_factory() for _ in range(3)]
        for i in items:
            ItemMovement.objects.create(session=cd,
                                        item=i,
                                        backoffice_user=user_factory(troubleshooter=True, superuser=True),
                                        amount=random.randint(1, i.initial_stock))
    return cd


def quota_factory(size=None):
    return Quota.objects.create(name='Day {} Quota'.format(random.randint(0, 4)),
                                size=random.randint(50, 300) if size is None else size)


def time_constraint_factory(active=True):
    fake = Faker('en-US')
    if active:
        start = fake.date_time_between(start_date='-23h', end_date='-1h')
        end = fake.date_time_between(start_date='+1h', end_date='+23h')
    else:
        start = fake.date_time_between(start_date='-23h', end_date='-10h')
        end = fake.date_time_between(start_date='-9h', end_date='-2h')
    return TimeConstraint.objects.create(name='Time Constraint',
                                         start=start,
                                         end=end)


def product_factory(items=False):
    fake = Faker('en-US')
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


def transaction_factory(session=None):
    return Transaction.objects.create(session=session or cashdesk_session_before_factory())


def transaction_position_factory(transaction=None, product=None):
    transaction = transaction or transaction_factory()
    product = product or product_factory(items=True)
    return TransactionPosition.objects.create(
        type='sell', value=product.price, tax_rate=product.tax_rate,
        product=product, transaction=transaction
    )


def warning_constraint_factory():
    return WarningConstraint.objects.create(
        name='U18 warning',
        message='Please check that the person is younger than 18 years old.'
    )


def list_constraint_factory(product=None, price=None):
    lc = ListConstraint.objects.create(
        name='VIP members'
    )
    if product:
        tax_rate = Decimal('19.00') if price else None
        ListConstraintProduct.objects.create(
            constraint=lc, product=product, price=price, tax_rate=tax_rate
        )
    return lc


def list_constraint_entry_factory(list_constraint, redeemed=False):
    fake = Faker('en-US')
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
