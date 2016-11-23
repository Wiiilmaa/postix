from django.db import models
from solo.models import SingletonModel


class EventSettings(SingletonModel):
    name = models.CharField(max_length=100, default='Generic Event')
    short_name = models.CharField(
        max_length=50,
        default='GE',
        help_text='A short name for your event.',
    )
    support_contact = models.CharField(
        max_length=200,
        default='Who is flying this thing? Enter your contact information as support contact info, please.',
        help_text='Your - yes YOUR - real-time contact info, e.g. phone number.',
    )
    invoice_address = models.CharField(max_length=200, blank=True, null=True)
    invoice_footer = models.CharField(max_length=200, blank=True, null=True)
    receipt_address = models.CharField(max_length=200, blank=True, null=True)
    receipt_footer = models.CharField(
        max_length=200,
        default='Thank you!',
        help_text='Use this to display additional disclaimers/data not in your address, such as VAT IDs.',
    )
    report_footer = models.CharField(
        max_length=500,
        default='CCC Veranstaltungsgesellschaft mbH',
        help_text='This will show up on backoffice session reports.'
    )
    initialized = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Event Settings'
