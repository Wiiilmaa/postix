import datetime
import random

from faker import Factory
import pytest


@pytest.fixture
def user():
    from .models import User
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
    from .models import Item
    fake = Factory.create('en-US')
    return Item(name=fake.state(),
                description=fake.bs(),
                inital_stock=random.randint(50, 1000))


@pytest.fixture
def cashdesk():
    from .models import Cashdesk
    fake = Factory.create('en-US')
    return Cashdesk(name='Cashdesk {}'.format(random.randint(0, 10)),
                    ip_adress=fake.ipv4(),
                    is_active=True)


@pytest.fixture
def cashdesk_session_before(cashdesk, user, superuser):
    from .models import CashdeskSession
    fake = Factory.create('en-US')
    cd = CashdeskSession(cashdesk=cashdesk,
                         user=user,
                         start=fake.date_time_this_month(),
                         cash_before=random.choice(50*i for i in range(6)),
                         backoffice_user_before=superuser)
    cd.items_before.add(item())
    cd.items_before.add(item())
    return cd


@pytest.fixture
def quota():
    from .models import Quota
    return Quota(name='Day {} Quota'.format(random.randint(0, 4)),
                 size=random.randint(50, 300))


@pytest.fixture
def time_constraint_active():
    from .models import TimeConstraint
    fake = Factory.create('en-US')
    start = fake.date_time_between(start='-23h', end='-1h')
    end = start + datetime.timedelta(hours=1)
    return TimeConstraint(name='Active Time Constraint', start=start, end=end)


@pytest.fixture
def time_constraint_passed():
    from .models import TimeConstraint
    fake = Factory.create('en-US')
    start = fake.date_time_between(start='-23h', end='-10h')
    end = fake.date_time_between(start='-9h', end='-2h')
    return TimeConstraint(name='Passed Time Constraint', start=start, end=end)
