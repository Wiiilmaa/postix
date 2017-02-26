import pytest

from postix.core.models import EventSettings


@pytest.fixture
def event_settings():
    return EventSettings.objects.get_or_create()
