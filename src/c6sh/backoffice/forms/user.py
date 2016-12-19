from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.urlresolvers import reverse


class CreateUserForm(forms.Form):
    username = forms.CharField(label='Username', max_length=254)
    password = forms.CharField(widget=forms.PasswordInput(), label='Passwort')
    firstname = forms.CharField(label='Vorname', max_length=254)
    lastname = forms.CharField(label='Nachname', max_length=254)
    is_backoffice_user = forms.BooleanField(label='Hinterzimmer-Rechte', required=False)
    is_troubleshooter = forms.BooleanField(label='Troubleshooter-Rechte', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'create_user_form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('backoffice:create-user')
        self.helper.add_input(Submit('submit', 'User anlegen'))
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'username',
            'password',
            'firstname',
            'lastname',
            'is_backoffice_user',
            'is_troubleshooter',
        )


def get_normal_user_form() -> CreateUserForm:
    form = CreateUserForm()
    form['is_backoffice_user'].widget = forms.HiddenInput()
    form['is_troubleshooter'].widget = forms.HiddenInput()
    form.helper.layout = Layout(
        'username',
        'password',
        'firstname',
        'lastname',
    )
    return form


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Password, again', widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.helper.add_input(Submit('submit', 'Reset password'))

    def is_valid(self):
        valid = super().is_valid()
        if valid:
            if self.cleaned_data.get('password1') == self.cleaned_data.get('password2'):
                return valid
            self._errors['incorrect_password'] = 'Passwords do not match!'
        return valid
