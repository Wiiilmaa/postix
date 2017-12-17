import pytest

from postix.troubleshooter.invoicing import generate_invoice

from ..factories import transaction_position_factory


@pytest.mark.django_db
def test_invoicing(event_settings):
    generate_invoice(transaction_position_factory().transaction, address='Foo\nBar\nBaz')
