import json

import pytest


def help_test_for_error(api, secret):
    response = api.post('/api/transactions/', {
        'positions': [
            {
                'type': 'redeem',
                'secret': secret
            }
        ]
    }, format='json')
    assert response.status_code == 400
    j = json.loads(response.content.decode())
    assert not j['success']
    assert not j['positions'][0]['success']
    return j['positions'][0]


@pytest.mark.django_db
def test_invalid(api_with_session, cashdesk_session_before):
    assert help_test_for_error(api_with_session, 'abcde') == {
        'success': False,
        'message': 'No ticket found with the given secret.',
        'type': 'error',
        'missing_field': None,
    }


@pytest.mark.django_db
def test_unpaid(api_with_session, preorder_position_unpaid):
    assert help_test_for_error(api_with_session, preorder_position_unpaid.secret) == {
        'success': False,
        'message': 'Ticket has not been paid for.',
        'type': 'error',
        'missing_field': None,
    }


@pytest.mark.django_db
def test_already_redeemed(api_with_session, preorder_position_redeemed):
    assert help_test_for_error(api_with_session, preorder_position_redeemed.secret) == {
        'success': False,
        'message': 'Ticket has already been redeemed.',
        'type': 'error',
        'missing_field': None,
    }
