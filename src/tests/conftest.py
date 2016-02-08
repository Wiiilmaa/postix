import datetime
import random
import string

from decimal import Decimal

from faker import Factory
import pytest


@pytest.fixture
def user():
    from c6sh.core.models import User
    fake = Factory.create('en-US')
    return User.objects.create(username=fake.user_name(),
                               password=fake.password(),
                               firstname=fake.first_name(),
                               lastname=fake.last_name(),
                               is_active=True,
                               is_superuser=False,
                               is_troubleshooter=False)


@pytest.fixture
def troubleshooter(user):
    user.is_troubleshooter = True
    return user


@pytest.fixture
def superuser(user):
    user.is_superuser = True
    return user


@pytest.fixture
def item_factory():
    from c6sh.core.models import Item

    def inner():
        fake = Factory.create('en-US')
        return Item.objects.create(name=fake.state(),
                                   description=fake.bs(),
                                   initial_stock=random.randint(50, 1000))
    return inner


@pytest.fixture
def cashdesk():
    from c6sh.core.models import Cashdesk
    fake = Factory.create('en-US')
    return Cashdesk.objects.create(name='Cashdesk {}'.format(random.randint(0, 10)),
                                   ip_address=fake.ipv4(),
                                   is_active=True)


@pytest.fixture
def cashdesk_session_before(cashdesk, user, superuser, item_factory):
    from c6sh.core.models import CashdeskSession, CashdeskSessionItem
    fake = Factory.create('en-US')
    cd = CashdeskSession.objects.create(cashdesk=cashdesk,
                                        user=user,
                                        start=fake.date_time_this_month(),
                                        cash_before=random.choice([50*i for i in range(6)]),
                                        backoffice_user_before=superuser)

    items = [item_factory() for _ in range(3)]
    for item in items:
        CashdeskSessionItem.objects.create(session=cd,
                                           item=item,
                                           amount_before=random.randint(1, item.initial_stock))
    return cd


@pytest.fixture
def quota():
    from c6sh.core.models import Quota
    return Quota.objects.create(name='Day {} Quota'.format(random.randint(0, 4)),
                                size=random.randint(50, 300))


@pytest.fixture
def time_constraint_active():
    from c6sh.core.models import TimeConstraint
    fake = Factory.create('en-US')
    start = fake.date_time_between(start='-23h', end='-1h')
    end = start + datetime.timedelta(hours=1)
    return TimeConstraint.objects.create(name='Active Time Constraint',
                                         start=start,
                                         end=end)


@pytest.fixture
def time_constraint_passed():
    from c6sh.core.models import TimeConstraint
    fake = Factory.create('en-US')
    start = fake.date_time_between(start='-23h', end='-10h')
    end = fake.date_time_between(start='-9h', end='-2h')
    return TimeConstraint.objects.create(name='Passed Time Constraint',
                                         start=start,
                                         end=end)


@pytest.fixture
def warning_constraint():
    from c6sh.core.models import WarningConstraint
    return WarningConstraint.objects.create(message='Does the person in front of you have a beard?')


@pytest.fixture
def list_constraint_with_entries():
    from c6sh.core.models import ListConstraint, ListConstraintEntry
    fake = Factory.create('en-US')
    l = ListConstraint.objects.create(name='VIP-Liste!!')
    [ListConstraintEntry.objects.create(list=l,
                                        name=fake.name(),
                                        identifier=random.randint(200, 1000))
        for _ in range(3)]
    return l


@pytest.fixture
def product_without_items():
    from c6sh.core.models import Product
    fake = Factory.create('en-US')
    return Product.objects.create(name=fake.catch_phrase(),
                                  price=random.choice([50*i for i in range(5)]),
                                  tax_rate=19)


@pytest.fixture
def product(product_without_items, item_factory):
    from c6sh.core.models import ProductItem
    ProductItem.objects.create(item=item_factory(), product=product_without_items,
                               amount=1)
    return product_without_items


@pytest.fixture
def preorder_unpaid():
    from c6sh.core.models import Preorder
    return Preorder.objects.create(order_code=''.join(random.choice(string.ascii_letters) for _ in range(24)))


@pytest.fixture
def preorder_paid(preorder_unpaid):
    preorder_unpaid.is_paid = True
    preorder_unpaid.save()
    return preorder_unpaid


@pytest.fixture
def preorder_position_paid(preorder_paid, product):
    from c6sh.core.models import PreorderPosition
    return PreorderPosition.objects.create(preorder=preorder_paid,
                                           secret=''.join(random.choice(string.ascii_letters) for _ in range(24)),
                                           product=product)


@pytest.fixture
def preorder_position_unpaid(preorder_unpaid, product):
    from c6sh.core.models import PreorderPosition
    return PreorderPosition.objects.create(preorder=preorder_unpaid,
                                           secret=''.join(random.choice(string.ascii_letters) for _ in range(24)),
                                           product=product)


@pytest.fixture
def transaction(cashdesk_session_before):
    from c6sh.core.models import Transaction
    return Transaction.objects.create(session=cashdesk_session_before)


@pytest.fixture
def preorder_position_redeemed(preorder_position_paid, transaction, product_without_items):
    from c6sh.core.models import TransactionPosition
    TransactionPosition.objects.create(
        type='redeem', preorder_position=preorder_position_paid,
        value=Decimal('0.00'), tax_rate=Decimal('0.00'), tax_value=Decimal('0.00'),
        product=product_without_items, transaction=transaction
    )
    return preorder_position_paid


@pytest.fixture
def warning_constraint():
    from c6sh.core.models import WarningConstraint
    return WarningConstraint.objects.create(
        name='U18 warning',
        message='Please check that the person is younger than 18 years old.'
    )


@pytest.fixture
def list_constraint():
    from c6sh.core.models import ListConstraint
    return ListConstraint.objects.create(
        name='CCC members'
    )


@pytest.fixture
def list_constraint_entry(list_constraint):
    from c6sh.core.models import ListConstraintEntry
    fake = Factory.create('en-US')
    return ListConstraintEntry.objects.create(
        list=list_constraint, name=fake.name(), identifier=str(random.randint(0, 100000))
    )


@pytest.fixture
def list_constraint_entry_redeemed(list_constraint_entry, product_without_items, transaction):
    from c6sh.core.models import TransactionPosition
    TransactionPosition.objects.create(
        type='redeem', listentry=list_constraint_entry,
        value=Decimal('0.00'), tax_rate=Decimal('0.00'), tax_value=Decimal('0.00'),
        product=product_without_items, transaction=transaction
    )
    return list_constraint_entry
