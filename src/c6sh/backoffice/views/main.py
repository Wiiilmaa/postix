from django.shortcuts import render
from .utils import backoffice_user_required


@backoffice_user_required
def main_view(request):
    return render(request, 'backoffice/main.html')
