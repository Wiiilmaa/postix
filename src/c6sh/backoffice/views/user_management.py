from typing import Union

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import ListView

from ...core.models import User
from ..forms import CreateUserForm, get_normal_user_form
from .utils import BackofficeUserRequiredMixin, backoffice_user_required


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


class UserListView(BackofficeUserRequiredMixin, ListView):
    template_name = 'backoffice/user_list.html'
    model = User
