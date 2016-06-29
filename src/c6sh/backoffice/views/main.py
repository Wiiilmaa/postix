from django.shortcuts import redirect

from .utils import backoffice_user_required


@backoffice_user_required
def main_view(request):
    return redirect('backoffice:session-list')
