import pytest

from ..factories import (
    cashdesk_factory, cashdesk_session_before_factory, user_factory,
)


@pytest.mark.django_db
def test_cashdesk_login(client):
    user = user_factory(password='trololol123')
    cashdesk_factory(ip='127.0.0.1')
    response = client.post('/login/', {'username': user.username, 'password': 'trololol123'}, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == '/login/'
    assert 'You do not have an active session' in response.content.decode()


@pytest.mark.django_db
def test_cashdesk_login_with_session(client):
    user = user_factory(password='trololol123')
    cashdesk_session_before_factory(ip='127.0.0.1', user=user)
    response = client.post('/login/', {'username': user.username, 'password': 'trololol123'}, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == '/'
    assert 'CHECKOUT' in response.content.decode()


@pytest.mark.django_db
def test_cashdesk_login_with_session_wrong_desk(client):
    user = user_factory(password='trololol123')
    cashdesk_factory(ip='127.0.0.1')
    cashdesk_session_before_factory(ip='10.0.0.2', user=user)
    response = client.post('/login/', {'username': user.username, 'password': 'trololol123'}, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == '/login/'
    assert 'different cashdesk. Please go to' in response.content.decode()
