from django import forms
from django.shortcuts import redirect, render

from ...core.models import User
from .utils import backoffice_user_required


@backoffice_user_required
def main_view(request):
    return render(request, 'backoffice/main.html')


class CreateUserForm(forms.Form):
    username = forms.CharField(label='Name', max_length=254)
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
