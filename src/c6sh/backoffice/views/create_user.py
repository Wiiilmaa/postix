from typing import Union

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from ...core.models import User
from .utils import backoffice_user_required


@backoffice_user_required
def main_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'backoffice/main.html')


@backoffice_user_required
def create_user_view(request: HttpRequest) -> Union[HttpResponseRedirect, HttpResponse]:
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            messages.success(request, '{} {} wurde angelegt.'.format(
                'Hinterzimmer-User' if user.is_backoffice_user else 'User',
                user.username,
            ))
            return redirect('backoffice:create-user')
    else:
        form = get_normal_user_form()

    return render(request, 'backoffice/create_user.html', {'form': form})
