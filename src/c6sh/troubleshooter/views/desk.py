from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from ...core.models import CashdeskSession, TroubleshooterNotification
from .utils import troubleshooter_user_required


@troubleshooter_user_required
def confirm_resupply(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    if request.method == 'POST':
        try:
            session = CashdeskSession.objects.get(pk=pk)
        except CashdeskSession.DoesNotExist:
            messages.error(request, _('Unknown session.'))
        else:
            TroubleshooterNotification.objects.active(session=session).update(
                status=TroubleshooterNotification.STATUS_ACK,
                modified_by=request.user
            )
            messages.success(request, _('{} has been resupplied.').format(session.cashdesk))

    return redirect('troubleshooter:main')
