from crispy_forms.helper import FormHelper
from django import forms

from postix.core.models import Asset, AssetPosition


class AssetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = Asset
        fields = '__all__'


class AssetMoveForm(forms.Form):
    identifier = forms.CharField(label='identifier', max_length=190, required=True)
    location = forms.CharField(label='location', max_length=190, required=False)
    comment = forms.CharField(label='comment', max_length=190, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class AssetHistoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = AssetPosition
        fields = '__all__'
