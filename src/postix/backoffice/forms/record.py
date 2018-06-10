from datetime import datetime

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from postix.core.models import Record, RecordEntity

User = get_user_model()


class RecordCreateForm(forms.ModelForm):
    backoffice_user = forms.CharField(max_length=254, label=_('Backoffice angel'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['backoffice_user'].queryset = User.objects.filter(is_backoffice_user=True)
        self.fields['datetime'].required = False
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_backoffice_user(self) -> User:
        value = self.cleaned_data['backoffice_user']
        try:
            return User.objects.filter(is_backoffice_user=True).get(username=value)
        except User.DoesNotExist:
            raise forms.ValidationError(_('Angel does not exist or is no backoffice angel.'))

    def clean_datetime(self) -> datetime:
        value = self.cleaned_data['datetime']
        return value or now()

    class Meta:
        model = Record
        fields = ('type', 'datetime', 'entity', 'carrier', 'amount', 'backoffice_user', )


class RecordEntityForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = RecordEntity
        fields = ('name', 'detail', )
