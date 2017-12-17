import pytest

from postix.core.models import EventSettings


@pytest.fixture
def event_settings():
    return EventSettings.objects.get_or_create()


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
