from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect

from .utils import backoffice_user_required


@backoffice_user_required
def main_view(request: HttpRequest) -> HttpResponseRedirect:
    return redirect('backoffice:session-list')
