import json

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from postix.core.models import Asset, AssetPosition


class AssetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("asset_type", "description", "identifier")

    class Meta:
        model = Asset
        fields = "__all__"


class AssetMoveForm(forms.Form):
    identifier = forms.CharField(label=_("QR code"), max_length=190, required=True)
    location = forms.CharField(label=_("Location"), max_length=190, required=False)
    comment = forms.CharField(label=_("Comment"), max_length=190, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("location", "comment", "identifier")


class AssetHistoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = AssetPosition
        fields = "__all__"


class AssetImportForm(forms.Form):
    asset_file = forms.FileField(
        label=_("Asset file"),
        help_text=_("A JSON file exported from another postix event."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Import assets")))

    def clean_asset_file(self):
        content = json.loads(self.cleaned_data["asset_file"].read().decode())
        if "assets" not in content:
            raise forms.ValidationError("Malformed asset file")
        return content

    def save(self):
        if not self.is_valid:
            raise Exception("Can only save a validated form.")

        import_data = self.cleaned_data["asset_file"]
        asset_list = []
        position_list = []
        for asset in import_data["assets"]:
            location = asset.pop("location")
            if (
                not location
            ):  # We only import assets that were returned at the end of last event
                asset_list.append(Asset(**asset))
        Asset.objects.bulk_create(asset_list)
        _now = now()
        for asset in Asset.objects.all():
            AssetPosition.objects.create(asset=asset, location="Import", start=_now)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs["accept"] = "text/*"
        return attrs
