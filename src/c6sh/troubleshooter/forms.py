from django import forms


class InvoiceAddressForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea)
