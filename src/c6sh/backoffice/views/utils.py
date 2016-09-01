from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin


def backoffice_user(user):
    if user.is_authenticated():
        return user.is_superuser or user.is_backoffice_user
    return False


class BackofficeUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return backoffice_user(self.request.user)


backoffice_user_required = user_passes_test(backoffice_user, login_url='backoffice:login')
