from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext as _

from c6sh.core.models import EventSettings


class EventSettingsForm(forms.ModelForm):
    class Meta:
        model = EventSettings
        exclude = []
        widgets = {
            'invoice_address': forms.widgets.Textarea,
            'invoice_footer': forms.widgets.Textarea,
            'receipt_address': forms.widgets.Textarea,
            'receipt_footer': forms.widgets.Textarea,
            'report_footer': forms.widgets.Textarea,
            'initialized': forms.widgets.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', _('Set up settings')))
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
