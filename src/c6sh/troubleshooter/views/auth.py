from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .utils import troubleshooter_user


class LoginView(TemplateView):
    template_name = 'troubleshooter/login.html'

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'No user account matches the entered credentials.')
            return redirect('troubleshooter:login')

        if not user.is_active:
            messages.error(request, 'User account is deactivated.')
            return redirect('troubleshooter:login')

        if not troubleshooter_user(user):
            messages.error(request, 'User does not have permission to access troubleshooter data.')
            return redirect('troubleshooter:login')

        login(request, user)
        return redirect('troubleshooter:main')


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    logout(request)
    return redirect('troubleshooter:login')
