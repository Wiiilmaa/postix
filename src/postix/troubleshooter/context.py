from ..core.models import TroubleshooterNotification


def processor(request):
    """
    Adds data to all template contexts
    """
    if not request.path.startswith('/troubleshooter'):
        return {}

    ctx = {}
    if TroubleshooterNotification.objects.active().exists():
        ctx['has_request'] = True

    return ctx
