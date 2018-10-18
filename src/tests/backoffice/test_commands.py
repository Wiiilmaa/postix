import pytest
from django.core.management import call_command

from postix.backoffice.report import generate_report

from ..factories import cashdesk_session_after_factory


@pytest.mark.django_db
def test_export_reports():
    generate_report(cashdesk_session_after_factory())
    call_command('export_reports')


@pytest.mark.django_db
def test_export_reports_with_fails():
    generate_report(cashdesk_session_after_factory())
    cashdesk_session_after_factory()
    call_command('export_reports')
