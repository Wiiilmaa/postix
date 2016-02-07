import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api():
    client = APIClient()
    return client


@pytest.fixture
def api_with_session(user, api, cashdesk_session_before):
    api.force_authenticate(user=cashdesk_session_before.user)
    return api