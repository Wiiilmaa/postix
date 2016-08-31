from crispy_forms.helper import FormHelper
from django import forms

from ..core.models import Cashdesk, Item, User


class SessionBaseForm(forms.Form):
    cashdesk = forms.ModelChoiceField(queryset=Cashdesk.objects.filter(is_active=True).order_by('name'), label='Kasse')
    user = forms.CharField(max_length=254, label='Engel')
    backoffice_user = forms.CharField(max_length=254, label='Hinterzimmer-Engel')
    cash_before = forms.DecimalField(max_digits=10, decimal_places=2, label='Bargeld')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_user(self):
        value = self.cleaned_data['user']
        try:
            return User.objects.get(username=value)
        except User.DoesNotExist:
            raise forms.ValidationError('Engel existiert nicht.')

    def clean_backoffice_user(self):
        value = self.cleaned_data['backoffice_user']
        try:
            return User.objects.filter(is_backoffice_user=True).get(username=value)
        except User.DoesNotExist:
            raise forms.ValidationError('Engel existiert nicht oder ist kein Hinterzimmer-Engel.')


class ItemMovementForm(forms.Form):
    """ This is basically only used in the formset below.
    Normally you would use a modelformset, but the Form helper class is
    required to correct some crispy_forms behaviour for now. """
    item = forms.ModelChoiceField(queryset=Item.objects.all().order_by('-initial_stock'), label='Produkt')
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


def get_form_and_formset(request=None, extra=1, initial_form=None, initial_formset=None):
    ItemMovementFormSet = forms.formset_factory(ItemMovementForm, extra=extra)

    if request:
        form = SessionBaseForm(request.POST, prefix='session')
        formset = ItemMovementFormSet(request.POST, prefix='items')
    elif initial_form or initial_formset:
        form = SessionBaseForm(initial=initial_form, prefix='session')
        formset = ItemMovementFormSet(initial=initial_formset, prefix='items')
    else:
        form = SessionBaseForm(prefix='session')
        formset = ItemMovementFormSet(prefix='items')
    return form, formset
