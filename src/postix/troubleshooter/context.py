from contextlib import suppress

from django.http import Http404
from django.urls import resolve

from ..core.models import TroubleshooterNotification


def processor(request):
    """
    Adds data to all template contexts
    """
    ctx = {
        "url_name": "",
        "url_namespace": "",
    }
    with suppress(Http404):
        url = resolve(request.path_info)
        ctx["url_name"] = url.url_name
        ctx["url_namespace"] = url.namespace

    if not request.path.startswith("/troubleshooter"):
        return ctx

    if TroubleshooterNotification.objects.active().exists():
        ctx["has_request"] = True
    return ctx
