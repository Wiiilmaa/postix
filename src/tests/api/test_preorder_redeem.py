import json

import pytest
from c6sh.core.models import WarningConstraintProduct, ListConstraintProduct


def help_test_for_error(api, secret, options=None):
    req = {
        'positions': [
            {
                'type': 'redeem',
                'secret': secret
            }
        ]
    }
    if options:
        req['positions'][0].update(options)
    response = api.post('/api/transactions/', req, format='json')
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


@pytest.mark.django_db
def test_preorder_warning(api_with_session, preorder_position_paid):
    preorder_position_paid.preorder.warning_text = "Foo"
    preorder_position_paid.preorder.save()
    assert help_test_for_error(api_with_session, preorder_position_paid.secret) == {
        'success': False,
        'message': 'Foo',
        'type': 'confirmation',
        'missing_field': 'warning_acknowledged',
    }


@pytest.mark.django_db
def test_preorder_warning_constraint(api_with_session, preorder_position_paid, warning_constraint):
    WarningConstraintProduct.objects.create(
        product=preorder_position_paid.product, constraint=warning_constraint
    )
    assert help_test_for_error(api_with_session, preorder_position_paid.secret) == {
        'success': False,
        'message': warning_constraint.message,
        'type': 'confirmation',
        'missing_field': 'warning_{}_acknowledged'.format(warning_constraint.pk),
    }


@pytest.mark.django_db
def test_preorder_list_constraint(api_with_session, preorder_position_paid, list_constraint):
    ListConstraintProduct.objects.create(
        product=preorder_position_paid.product, constraint=list_constraint
    )
    assert help_test_for_error(api_with_session, preorder_position_paid.secret) == {
        'success': False,
        'message': 'This ticket can only redeemed by persons on the list "{}".'.format(list_constraint.name),
        'type': 'input',
        'missing_field': 'list_{}'.format(list_constraint.pk),
    }


@pytest.mark.django_db
def test_preorder_list_constraint_unknown(api_with_session, preorder_position_paid, list_constraint):
    ListConstraintProduct.objects.create(
        product=preorder_position_paid.product, constraint=list_constraint,
    )
    options = {
        'list_{}'.format(list_constraint.pk): '2'
    }
    assert help_test_for_error(api_with_session, preorder_position_paid.secret, options) == {
        'success': False,
        'message': 'Entry not found on list "{}".'.format(list_constraint.name),
        'type': 'input',
        'missing_field': 'list_{}'.format(list_constraint.pk),
    }


@pytest.mark.django_db
def test_preorder_list_constraint_used(api_with_session, preorder_position_paid, list_constraint_entry_redeemed):
    ListConstraintProduct.objects.create(
        product=preorder_position_paid.product, constraint=list_constraint_entry_redeemed.list,
    )
    options = {
        'list_{}'.format(list_constraint_entry_redeemed.list.pk): str(list_constraint_entry_redeemed.id)
    }
    assert help_test_for_error(api_with_session, preorder_position_paid.secret, options) == {
        'success': False,
        'message': 'This list entry already has been used.'.format(list_constraint_entry_redeemed.list.name),
        'type': 'input',
        'missing_field': 'list_{}'.format(list_constraint_entry_redeemed.list.pk),
    }
