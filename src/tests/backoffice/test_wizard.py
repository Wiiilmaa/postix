import pytest


@pytest.mark.parametrize('url,expected', (
    ('/backoffice/', 200),
    ('/backoffice/session/new/', 200),
    ('/backoffice/session/', 200),
    ('/backoffice/reports/', 200),
    ('/backoffice/create_user/', 200),
    ('/backoffice/users/', 200),
    ('/backoffice/wizard/users/', 302),
    ('/backoffice/wizard/settings/', 302),
    ('/backoffice/wizard/cashdesks/', 302),
    ('/backoffice/wizard/import/', 302),
    ('/backoffice/wizard/items/', 302),
    ('/backoffice/wizard/items/new', 302),
))
@pytest.mark.django_db
def test_can_access_pages(backoffice_client, url, expected):
    response = backoffice_client.get(url)
    assert response.status_code == expected
    if expected == 200:
        assert 'Please call a superuser to initialize this event\'s settings.' in response.content.decode()
