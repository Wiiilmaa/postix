import pytest
from tests.factories import cashdesk_session_before_factory


@pytest.mark.django_db
def test_get_current_session():
    # todo: add old session as soon as cashdesk_session_old fixture is done
    session = cashdesk_session_before_factory()
    user = session.user
    assert user.get_current_session() == session
