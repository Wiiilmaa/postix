from django import forms

from c6sh.core.models import Cashdesk


class InvoiceAddressForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea)


class CashdeskForm(forms.Form):
    cashdesk = forms.ModelChoiceField(queryset=Cashdesk.objects.all())


class PrintForm(forms.Form):
    cashdesk = forms.ModelChoiceField(queryset=Cashdesk.objects.all())
    amount = forms.IntegerField(min_value=1, max_value=50)
