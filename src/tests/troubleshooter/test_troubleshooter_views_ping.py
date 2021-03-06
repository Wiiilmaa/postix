import pytest

from postix.core.models import Ping

from ..factories import cashdesk_factory, ping_factory


@pytest.mark.django_db
def test_troubleshooter_ping_view(troubleshooter_client):
    [ping_factory(ponged=(index % 3 != 0)) for index in range(10)]
    desk = cashdesk_factory()
    assert Ping.objects.count() == 10
    response = troubleshooter_client.get("/troubleshooter/ping/")
    assert response.status_code == 200
    response = troubleshooter_client.post(
        "/troubleshooter/ping/", {"cashdesk": desk.pk}, follow=True
    )
    assert response.status_code == 200
    assert Ping.objects.count() == 11


@pytest.mark.django_db
def test_troubleshooter_ping_view_no_responses(troubleshooter_client):
    ping_factory(ponged=None)
    cashdesk_factory()
    assert Ping.objects.count() == 1
    response = troubleshooter_client.get("/troubleshooter/ping/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_troubleshooter_ping_view_wrong_pong(troubleshooter_client):
    desk = cashdesk_factory()
    response = troubleshooter_client.post(
        "/troubleshooter/ping/", {"cashdesk": desk.pk + 5}, follow=True
    )
    assert response.status_code == 200
    assert Ping.objects.count() == 0
