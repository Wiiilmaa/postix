import pytest


@pytest.mark.django_db
def test_get_current_session(cashdesk_session_before, user):
    # todo: add old session as soon as cashdesk_session_old fixture is done
    user = cashdesk_session_before.user
    assert user.get_current_session() == cashdesk_session_before
