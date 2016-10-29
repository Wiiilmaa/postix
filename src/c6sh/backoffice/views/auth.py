from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.http import is_safe_url
from django.views.generic import TemplateView

from .utils import is_backoffice_user


class LoginView(TemplateView):
    template_name = 'backoffice/login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'No user account matches the entered credentials.')
            return redirect('backoffice:login')

        if not user.is_active:
            messages.error(request, 'User account is deactivated.')
            return redirect('backoffice:login')

        if not is_backoffice_user(user):
            messages.error(request, 'User does not have permission to access backoffice data.')
            return redirect('backoffice:login')

        login(request, user)
        url = request.GET.get('next')
        if url and is_safe_url(url, request.get_host()):
            return redirect(url)

        return redirect('backoffice:main')


def logout_view(request):
    logout(request)
    return redirect('backoffice:login')


def switch_user(request):
    logout(request)
    return redirect(reverse('backoffice:login') + '?next=' + request.GET.get('next', ''))
