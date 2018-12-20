import pytest
from rest_framework.test import APIClient

from ..factories import cashdesk_session_before_factory


@pytest.fixture
def api():
    client = APIClient()
    return client


@pytest.fixture
def session():
    return cashdesk_session_before_factory()


@pytest.fixture
def api_with_session(api, session):
    api.force_authenticate(user=session.user)
    return api
