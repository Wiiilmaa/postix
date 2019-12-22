from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, FormView, ListView, UpdateView, View

from postix.backoffice.forms.asset import AssetForm, AssetImportForm, AssetMoveForm
from postix.core.models import Asset, AssetPosition, EventSettings

from .utils import BackofficeUserRequiredMixin, SuperuserRequiredMixin


class AssetListView(BackofficeUserRequiredMixin, ListView):
    model = Asset
    queryset = Asset.objects.all()
    template_name = "backoffice/asset_list.html"
    context_object_name = "assets"


class AssetCreateView(BackofficeUserRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "backoffice/new_asset.html"

    def get_success_url(self):
        return reverse("backoffice:asset-list")


class AssetUpdateView(BackofficeUserRequiredMixin, UpdateView):
    model = Asset
    queryset = Asset.objects.all()
    form_class = AssetForm
    template_name = "backoffice/new_asset.html"

    def get_success_url(self):
        return reverse("backoffice:asset-list")


class AssetMoveView(BackofficeUserRequiredMixin, FormView):
    form_class = AssetMoveForm
    template_name = "backoffice/move_asset.html"

    def get_success_url(self):
        return reverse("backoffice:asset-list")

    def form_valid(self, form):
        asset = Asset.objects.filter(identifier=form.cleaned_data["identifier"]).first()
        if not asset:
            messages.error(self.request, _("Unknown asset"))
            return self.form_invalid(form)
        position = asset.get_current_position()
        location = form.cleaned_data["location"]
        comment = form.cleaned_data["comment"]
        if not location:
            if not position:
                messages.error(
                    self.request,
                    _("Asset was not marked as away, does not need to be returned"),
                )
                return self.form_invalid(form)
            position.end = now()
            position.comment = comment
            asset.last_seen = now()
            position.save()
            asset.save()
            return redirect(self.get_success_url())
        else:
            if position:
                position.end = now()
                asset.last_seen = now()
                position.save()
                asset.save()
            AssetPosition.objects.create(
                asset=asset, start=now(), location=location, comment=comment
            )
            return redirect(self.get_success_url())


class AssetHistoryView(BackofficeUserRequiredMixin, ListView):
    queryset = AssetPosition.objects.all().order_by("-start")
    template_name = "backoffice/asset_history.html"
    context_object_name = "history"


class AssetExportView(SuperuserRequiredMixin, View):
    def dispatch(self, request):
        data = {
            "assets": [
                {
                    "identifier": asset.identifier,
                    "asset_type": asset.asset_type,
                    "description": asset.description,
                    "created": asset.created,
                    "last_seen": asset.last_seen,
                    "location": getattr(asset.get_current_position(), "location", None),
                }
                for asset in Asset.objects.all()
            ]
        }
        settings = EventSettings.get_solo()
        response = JsonResponse(data)
        filename = (
            settings.short_name
            + "_assets_"
            + now().strftime("%Y-%m-%d-%H-%M")
            + ".json"
        )
        response["Content-Disposition"] = 'attachment; filename="' + filename + '"'


class AssetExportView(SuperuserRequiredMixin, View):
    def dispatch(self, request):
        data = {
            "assets": [
                {
                    "identifier": asset.identifier,
                    "asset_type": asset.asset_type,
                    "description": asset.description,
                    "created": asset.created,
                    "last_seen": asset.last_seen,
                    "location": getattr(asset.get_current_position(), "location", None),
                }
                for asset in Asset.objects.all()
            ]
        }
        settings = EventSettings.get_solo()
        response = JsonResponse(data)
        filename = (
            settings.short_name
            + "_assets_"
            + now().strftime("%Y-%m-%d-%H-%M")
            + ".json"
        )
        response["Content-Disposition"] = 'attachment; filename="' + filename + '"'
        return response


class AssetImportView(SuperuserRequiredMixin, FormView):
    form_class = AssetImportForm
    template_name = "backoffice/asset_import.html"

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, _("The assets have been imported, please double-check them.")
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return redirect("backoffice:asset-import")

    def get_success_url(self):
        return reverse("backoffice:asset-list")
