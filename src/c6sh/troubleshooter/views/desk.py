from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect

from ...core.models import CashdeskSession, TroubleshooterNotification
from .utils import troubleshooter_user_required


@troubleshooter_user_required
def confirm_resupply(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    if request.method == 'POST':
        try:
            session = CashdeskSession.objects.get(pk=pk)
        except CashdeskSession.DoesNotExist:
            messages.error(request, 'Session nicht bekannt.')
        else:
            TroubleshooterNotification.objects.active(session=session).update(
                status=TroubleshooterNotification.STATUS_ACK,
                modified_by=request.user
            )
            messages.success(request, '{} wurde versorgt \o/'.format(session.cashdesk))

    return redirect('troubleshooter:main')
