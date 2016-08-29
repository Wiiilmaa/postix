from django.shortcuts import render

from .utils import troubleshooter_user_required
from ...core.models import Cashdesk


@troubleshooter_user_required
def main_view(request):
    ctx = {}

    sessions = []
    for c in Cashdesk.objects.filter(is_active=True).order_by('name'):
        for sess in c.get_active_sessions():
            sess.current_items = sess.get_current_items()
            sessions.append(sess)

    ctx['sessions'] = sessions

    return render(request, 'troubleshooter/main.html', ctx)
