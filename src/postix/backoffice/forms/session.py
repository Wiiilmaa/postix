from typing import Any, Tuple

from crispy_forms.helper import FormHelper
from django import forms
from django.http import HttpRequest
from django.utils.translation import ugettext as _

from postix.core.models import Cashdesk, Item, User


class CalculatorWidget(forms.NumberInput):

    def __init__(self, *args, attrs=None, **kwargs):
        attrs = attrs or dict()
        attrs['type'] = 'text'
        attrs['class'] = 'calculatable'
        super().__init__(*args, attrs=attrs, **kwargs)


class RelaxedDecimalField(forms.DecimalField):
    widget = CalculatorWidget

    def to_python(self, value):
        return super().to_python(
            value.replace(",", ".") if isinstance(value, str) else value
        )

    def validate(self, value):
        return super().validate(
            value.replace(",", ".") if isinstance(value, str) else value
        )


class SessionBaseForm(forms.Form):
    cashdesk = forms.ModelChoiceField(
        queryset=Cashdesk.objects.filter(is_active=True).order_by('name'),
        label=_('Cashdesk'),
    )
    user = forms.CharField(max_length=254, label=_('Angel'))
    backoffice_user = forms.CharField(max_length=254, label=_('Backoffice angel'))
    cash_before = RelaxedDecimalField(
        max_digits=10,
        decimal_places=2,
        label=_('Cash'),
    )

    def __init__(self, *args, must_be_positive=False, **kwargs):
        initial = kwargs.get('initial', dict())
        super().__init__(*args, **kwargs)
        self.must_be_positive = must_be_positive
        if must_be_positive:
            self.fields['cash_before'].widget.attrs['min'] = '0'
        self.fields['user'].required = (
            initial.get('cashdesk') and initial['cashdesk'].ip_address
        )
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_user(self) -> User:
        value = self.cleaned_data['user']
        if self.cleaned_data['cashdesk'].ip_address:
            try:
                return User.objects.get(username=value)
            except User.DoesNotExist:
                raise forms.ValidationError(_('Angel does not exist.'))
        return value

    def clean_backoffice_user(self) -> User:
        value = self.cleaned_data['backoffice_user']
        try:
            return User.objects.filter(is_backoffice_user=True).get(username=value)
        except User.DoesNotExist:
            raise forms.ValidationError(
                _('Angel does not exist or is no backoffice angel.')
            )

    def clean_cash_before(self):
        value = self.cleaned_data['cash_before']
        if self.must_be_positive and value < 0:
            raise forms.ValidationError(_('Please supply a positive amount of cash.'))
        return value


class ItemMovementForm(forms.Form):
    """ This is basically only used in the formset below.
    Normally you would use a modelformset, but the Form helper class is
    required to correct some crispy_forms behaviour for now. """

    item = forms.ModelChoiceField(
        queryset=Item.objects.all().order_by('-initial_stock'), label=_('Product')
    )
    amount = forms.IntegerField(label='Anzahl')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.tag = 'td'
        self.helper.form_show_labels = False


class ItemMovementFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = 'bootstrap/table_inline_formset.html'
        self.form_id = 'session-items'
        self.form_tag = False


def get_form_and_formset(
    request: HttpRequest = None,
    extra: int = 1,
    initial_form: SessionBaseForm = None,
    initial_formset=None,
    must_be_positive=False,
) -> Tuple[SessionBaseForm, Any]:
    ItemMovementFormSet = forms.formset_factory(ItemMovementForm, extra=extra)

    if request:
        form = SessionBaseForm(
            request.POST, prefix='session', must_be_positive=must_be_positive
        )
        formset = ItemMovementFormSet(request.POST, prefix='items')
    else:
        form = SessionBaseForm(
            initial=initial_form, prefix='session', must_be_positive=must_be_positive
        )
        formset = ItemMovementFormSet(initial=initial_formset, prefix='items')
    return form, formset
