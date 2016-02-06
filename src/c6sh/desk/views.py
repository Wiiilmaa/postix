from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = 'desk/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                messages.error(request, 'User account is deactivated.')
        else:
            messages.error(request, 'No user account matches the entered credentials.')
            return redirect('desk:login')


@login_required(login_url='/login/')
def main_view(request):
    pass
