from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext as _

from postix.core.models import (
    Cashdesk, EventSettings, Item, Product, ProductItem,
)


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


class CashdeskForm(forms.ModelForm):

    class Meta:
        model = Cashdesk
        fields = (
            'name', 'ip_address', 'printer_queue_name', 'printer_handles_drawer'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', _('Add Cashdesk')))
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'


class ImportForm(forms.Form):

    _file = forms.FileField(label=_('JSON File'))
    cashdesks = forms.IntegerField(min_value=0, required=False, label=_('Create cashdesks'), help_text=_('If you do not have any cashdesks yet, create them'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', _('Import presale export')))
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'


class ItemForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Item
        fields = (
            'name', 'description', 'initial_stock',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            valid_products = ProductItem.objects.filter(item=self.instance).values_list('product_id', flat=True)
            self.initial['products'] = Product.objects.filter(pk__in=valid_products)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', _('Save Item')))
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

    def save(self, *args, **kwargs):
        ret = super().save(*args, **kwargs)
        old_products = set(ProductItem.objects.filter(item=ret).values_list('product', flat=True))
        new_products = set(self.cleaned_data['products'])

        for product in old_products - new_products:
            ProductItem.objects.filter(product=product, item=ret).delete()
        for product in new_products - old_products:
            ProductItem.objects.create(product=product, item=ret, amount=1)
        return ret
