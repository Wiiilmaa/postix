from datetime import timedelta

import pytest
from django.utils.timezone import now
from faker import Factory
from tests.factories import cashdesk_session_before_factory


@pytest.mark.django_db
def test_session_active():
    session = cashdesk_session_before_factory()
    assert session.is_active()


@pytest.mark.django_db
def test_session_not_active():
    session = cashdesk_session_before_factory()
    session.end = now() - timedelta(hours=1)
    assert not session.is_active()
