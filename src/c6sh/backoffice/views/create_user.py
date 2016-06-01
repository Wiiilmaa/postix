from django import forms
from django.shortcuts import redirect, render

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from ...core.models import User
from .utils import backoffice_user_required


@backoffice_user_required
def main_view(request):
    return render(request, 'backoffice/main.html')


class CreateUserForm(forms.Form):
    username = forms.CharField(label='Username', max_length=254)
    password = forms.CharField(widget=forms.PasswordInput(), label='Passwort')
    firstname = forms.CharField(label='Vorname', max_length=254)
    lastname = forms.CharField(label='Nachname', max_length=254)
    is_backoffice_user = forms.BooleanField(label='Hinterzimmer-Rechte', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'create_user_form'
        self.helper.form_method = 'post'
        self.helper.form_action = 'create_user'
        self.helper.add_input(Submit('submit', 'User anlegen'))
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'username',
            'password',
            'firstname',
            'lastname',
            'is_backoffice_user',
        )


@backoffice_user_required
def create_user_view(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.pop('is_backoffice_user'):
                User.objects.create_superuser(**form.cleaned_data)
            else:
                User.objects.create_user(**form.cleaned_data)
            return redirect('backoffice:main')
    else:
        form = CreateUserForm()

    return render(request, 'backoffice/create_user.html', {'form': form})
