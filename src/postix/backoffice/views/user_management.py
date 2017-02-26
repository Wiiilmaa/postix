from typing import Union

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.views.generic import FormView, ListView

from ...core.models import User
from ..forms import CreateUserForm, ResetPasswordForm, get_normal_user_form
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
            if user.is_backoffice_user:
                messages.success(request, _('Backoffice user {user} has been created.').format(user.username))
            else:
                messages.success(request, _('User {user} has been created.').format(user.username))
            return redirect('backoffice:create-user')
    else:
        form = get_normal_user_form()

    return render(request, 'backoffice/create_user.html', {'form': form})


class UserListView(BackofficeUserRequiredMixin, ListView):
    template_name = 'backoffice/user_list.html'
    queryset = User.objects.all().order_by('username')


class ResetPasswordView(BackofficeUserRequiredMixin, FormView):
    form_class = ResetPasswordForm
    template_name = 'backoffice/reset_password.html'

    def get_context_data(self):
        pk = self.kwargs['pk']
        ctx = super().get_context_data()
        ctx['user'] = User.objects.get(pk=pk)
        return ctx

    def post(self, request, pk):
        form = self.get_form()
        pk = self.kwargs['pk']
        user = User.objects.get(pk=pk)
        if user.is_superuser and not request.user.is_superuser:
            messages.error(self.request, _('You can only change administrator passwords if you are an admin yourself.'))
            return self.form_valid(form)

        if form.is_valid():
            user.set_password(form.cleaned_data.get('password1'))
            user.save()
            messages.success(self.request, _('Passwort has been changed.'))
            return self.form_valid(form)

    def get_success_url(self):
        return reverse('backoffice:user-list')
