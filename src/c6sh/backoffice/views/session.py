import json

from django import forms
from django.contrib import messages
from django.core import serializers
from django.shortcuts import render
from django.utils.timezone import now

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from ...core.models import Cashdesk, CashdeskSession, CashdeskSessionItem, Item, User


class NewSessionItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all().order_by('-initial_stock'), label='Produkt')
    amount = forms.IntegerField(min_value=0, label='Anzahl')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap/field.html'
        self.helper.form_tag = False
        self.helper.tag = 'td'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            'cashdesk',
            'user',
            'cash_before',
        )


NewSessionFormSet = forms.formset_factory(NewSessionItemForm)


class NewSessionItemFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = 'bootstrap/table_inline_formset.html'
        self.form_id = 'session-items'
        self.form_tag = False


class SessionBaseForm(forms.Form):
    cashdesk = forms.ModelChoiceField(queryset=Cashdesk.objects.filter(is_active=True).order_by('name'), label='Kasse')
    user = forms.CharField(max_length=254, label='Engel')
    cash_before = forms.DecimalField(max_digits=10, decimal_places=2, label='Bargeld')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


def new_session(request):
    pass


def end_session(request):
    pass


def resupply_session(request):
    pass


def edit_session(request):
    pass
