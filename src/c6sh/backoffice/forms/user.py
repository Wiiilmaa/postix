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
