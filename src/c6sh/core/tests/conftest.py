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
    return CashdeskSession(cashdesk=cashdesk,
                           user=user,
                           start=fake.date_time_this_month(),
                           cash_before=random.choice(50*i for i in range(6)),
                           backoffice_user_before=superuser)
