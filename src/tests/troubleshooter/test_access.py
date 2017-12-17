import pytest


@pytest.mark.parametrize('url,expected', (
    ('/backoffice/', 302),
    ('/troubleshooter/', 200),
    ('/troubleshooter/transactions/', 200),
    ('/troubleshooter/constraints/', 200),
    ('/troubleshooter/preorders/', 200),
    ('/troubleshooter/ping/', 200),
    ('/troubleshooter/information/', 200),
))
@pytest.mark.django_db
def test_can_access_pages(troubleshooter_client, url, expected):
    response = troubleshooter_client.get(url)
    assert response.status_code == expected
    if expected == 200:
        assert 'Troubleshooter' in response.content.decode()

