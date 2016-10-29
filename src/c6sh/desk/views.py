from typing import Union

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.views.generic import TemplateView

from ..core.utils.iputils import detect_cashdesk, get_ip_address
from ..core.models import Cashdesk


class LoginView(TemplateView):
    template_name = 'desk/login.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> Union[HttpResponseRedirect, HttpResponse]:
        if not self.cashdesk:
            return render(request, 'desk/fail.html', {
                'message': 'This is not a registered cashdesk.',
                'detail': 'Your IP address is {0}'.format(get_ip_address(request))
            })
        if request.user.is_authenticated():
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, 'User account is deactivated.')
                return redirect('desk:login')

            session = user.get_current_session()
            if session is None:
                messages.error(request, 'You do not have an active session.')
                return redirect('desk:login')

            if session.cashdesk != self.cashdesk:
                messages.error(request, 'Your session is scheduled for a different cashdesk.')
                return redirect('desk:login')

            login(request, user)
            session.cashdesk.display.next()
            return redirect('desk:main')
        else:
            messages.error(request, 'No user account matches the entered credentials.')
        return redirect('desk:login')

    @cached_property
    def cashdesk(self) -> Cashdesk:
        return detect_cashdesk(self.request)


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    session = request.user.get_current_session()
    logout(request)
    session.cashdesk.display.close()
    return redirect('desk:login')


@login_required(login_url='/login/')
def main_view(request: HttpRequest) -> HttpResponse:
    cashdesk = detect_cashdesk(request)
    session = request.user.get_current_session()
    if not cashdesk or session is None or session.cashdesk != cashdesk:
        return render(request, 'desk/fail.html', {
            'message': 'You do not have an active session at this cashdesk.',
            'detail': 'You are logged in as {}.'.format(request.user),
            'offer_logout': True
        })

    if not session.start:
        session.start = now()
        session.save(update_fields=['start'])

    return render(request, 'desk/main.html')
