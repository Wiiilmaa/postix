import pytest

from c6sh.core.models import EventSettings


@pytest.fixture
def event_settings():
    return EventSettings.objects.get_or_create()
