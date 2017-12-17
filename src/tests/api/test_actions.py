import json

import pytest

from ..factories import ping_factory, transaction_factory


@pytest.mark.django_db
def test_open_drawer(api_with_session):
    response = api_with_session.post('/api/cashdesk/open-drawer/')
    content = json.loads(response.content.decode())
    assert content == {'success': True}


@pytest.mark.django_db
def test_reprint_receipt(api_with_session):
    transaction = transaction_factory()
    response = api_with_session.post('/api/cashdesk/reprint-receipt/', {'transaction': transaction.id})
    content = json.loads(response.content.decode())
    assert content == {'success': True}


@pytest.mark.django_db
def test_reprint_receipt_fail(api_with_session):
    transaction = transaction_factory()
    response = api_with_session.post('/api/cashdesk/reprint-receipt/', {'transaction': transaction.id + 1337})
    content = json.loads(response.content.decode())
    assert content == {'success': False, 'error': 'Transaction not found.'}


@pytest.mark.django_db
def test_signal_next(api_with_session):
    response = api_with_session.post('/api/cashdesk/signal-next/')
    content = json.loads(response.content.decode())
    assert content == {'success': True}


@pytest.mark.django_db
def test_print_ping(api_with_session):
    response = api_with_session.post('/api/cashdesk/print-ping/')
    content = json.loads(response.content.decode())
    assert content == {'success': True}


@pytest.mark.django_db
def test_pong_ping(api_with_session):
    p = ping_factory()
    response = api_with_session.post('/api/cashdesk/pong/', {'pong': p.secret})
    content = json.loads(response.content.decode())
    assert content == {'success': True}
    p.refresh_from_db()
    assert p.ponged
