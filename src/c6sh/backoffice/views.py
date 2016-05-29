from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from ..core.models import User


def backoffice_user(user):
    return user.is_superuser


backoffice_user_required = user_passes_test(backoffice_user, login_url='backoffice:login')


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

        if not backoffice_user(user):
            messages.error(request, 'User does not have permission to access backoffice data.')
            return redirect('backoffice:login')

        login(request, user)
        return redirect('backoffice:main')


def logout_view(request):
    logout(request)
    return redirect('backoffice:login')


@backoffice_user_required
def main_view(request):
    return render(request, 'backoffice/main.html')


class CreateUserForm(forms.Form):
    username = forms.CharField(label='Name')
    password = forms.CharField(widget=forms.PasswordInput(), label='Passwort')
    is_backoffice_user = forms.BooleanField(label='Hinterzimmer-Rechte', required=False)


@backoffice_user_required
def create_user_view(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.pop('is_backoffice_user'):
                new_user = User.objects.create_superuser(**form.cleaned_data)
            else:
                new_user = User.objects.create_user(**form.cleaned_data)
            return redirect('backoffice:main')
    else:
        form = CreateUserForm()

    return render(request, 'backoffice/create_user.html', {'form': form})
