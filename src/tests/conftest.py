import pytest

from postix.core.models import EventSettings


@pytest.fixture
def event_settings():
    settings = EventSettings.get_solo()
    settings.invoice_address = 'Foo Conferences\n42 Bar St\nBaz City'
    settings.initialized = True
    settings.save()
    return settings


@pytest.fixture
def troubleshooter_client(client):
    from .factories import user_factory

    user = user_factory(troubleshooter=True)
    client.force_login(user)
    return client


@pytest.fixture
def backoffice_client(client):
    from .factories import user_factory

    user = user_factory(backoffice=True)
    client.force_login(user)
    return client


@pytest.fixture
def superuser_client(client):
    from .factories import user_factory

    user = user_factory(superuser=True)
    client.force_login(user)
    return client
