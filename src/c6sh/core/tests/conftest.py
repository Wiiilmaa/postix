import datetime
import random

from faker import Factory
import pytest


@pytest.fixture
def user():
    from c6sh.core.models import User
    fake = Factory.create('en-US')
    return User(username=fake.user_name(),
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
def item():
    from c6sh.core.models import Item
    fake = Factory.create('en-US')
    return Item(name=fake.state(),
                description=fake.bs(),
                initial_stock=random.randint(50, 1000))


@pytest.fixture
def cashdesk():
    from c6sh.core.models import Cashdesk
    fake = Factory.create('en-US')
    return Cashdesk(name='Cashdesk {}'.format(random.randint(0, 10)),
                    ip_address=fake.ipv4(),
                    is_active=True)


@pytest.fixture
def cashdesk_session_before(cashdesk, user, superuser):
    from c6sh.core.models import CashdeskSession, CashdeskSessionItem
    fake = Factory.create('en-US')
    cd = CashdeskSession(cashdesk=cashdesk,
                         user=user,
                         start=fake.date_time_this_month(),
                         cash_before=random.choice([50*i for i in range(6)]),
                         backoffice_user_before=superuser)

    items = [item() for _ in range(3)]
    c = [CashdeskSessionItem(session=cd, item=i, amount_before=random.randint(1, i.initial_stock)) for i in items]
    return cd


@pytest.fixture
def quota():
    from c6sh.core.models import Quota
    return Quota(name='Day {} Quota'.format(random.randint(0, 4)),
                 size=random.randint(50, 300))


@pytest.fixture
def time_constraint_active():
    from c6sh.core.models import TimeConstraint
    fake = Factory.create('en-US')
    start = fake.date_time_between(start='-23h', end='-1h')
    end = start + datetime.timedelta(hours=1)
    return TimeConstraint(name='Active Time Constraint', start=start, end=end)


@pytest.fixture
def time_constraint_passed():
    from c6sh.core.models import TimeConstraint
    fake = Factory.create('en-US')
    start = fake.date_time_between(start='-23h', end='-10h')
    end = fake.date_time_between(start='-9h', end='-2h')
    return TimeConstraint(name='Passed Time Constraint', start=start, end=end)
