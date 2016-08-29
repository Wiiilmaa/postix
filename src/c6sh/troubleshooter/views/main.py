from django.shortcuts import render

from .utils import troubleshooter_user_required


@troubleshooter_user_required
def main_view(request):
    return render(request, 'troubleshooter/main.html', {})
