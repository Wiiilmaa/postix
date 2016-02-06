from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.views.generic import TemplateView

from ..core.models import Cashdesk


def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')


def detect_cashdesk(request):
    try:
        return Cashdesk.objects.get(ip_address=get_ip_address(request))
    except Cashdesk.DoesNotExist:
        return None


class LoginView(TemplateView):
    template_name = 'desk/login.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.cashdesk:
            return render(request, 'desk/fail.html', {
                'message': 'This is not a registered cashdesk.',
                'detail': 'Your IP address is {0}'.format(get_ip_address(request))
            })
        if request.user.is_authenticated():
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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
            return redirect('desk:main')
        else:
            messages.error(request, 'No user account matches the entered credentials.')
        return redirect('desk:login')

    @cached_property
    def cashdesk(self):
        return detect_cashdesk(self.request)


def logout_view(request):
    logout(request)
    return redirect('desk:login')


@login_required(login_url='/login/')
def main_view(request):
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
        session.save()

    return render(request, 'desk/main.html')