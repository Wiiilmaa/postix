import json
import pytest


@pytest.mark.django_db
def test_preorder_redeem_invalid(api_with_session, cashdesk_session_before):
    response = api_with_session.post('/api/transactions/', {
        'positions': [
            {
                'type': 'redeem',
                'secret': 'ABCDE'
            }
        ]
    }, format='json')
    assert response.status_code == 400
    assert json.loads(response.content.decode()) == {
        'success': False,
        'positions': [
            {
                'success': False,
                'message': 'No ticket found with the given secret.',
                'type': 'error',
                'missing_field': None,
            }
        ]
    }


@pytest.mark.django_db
def test_preorder_redeem_unpaid(api_with_session, preorder_position_unpaid):
    response = api_with_session.post('/api/transactions/', {
        'positions': [
            {
                'type': 'redeem',
                'secret': preorder_position_unpaid.secret
            }
        ]
    }, format='json')
    assert response.status_code == 400
    assert json.loads(response.content.decode()) == {
        'success': False,
        'positions': [
            {
                'success': False,
                'message': 'Ticket has not been paid for.',
                'type': 'error',
                'missing_field': None,
            }
        ]
    }
