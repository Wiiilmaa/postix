from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

from c6sh.core.models import User


def is_backoffice_user(user: User) -> bool:
    if user.is_authenticated():
        return user.is_superuser or user.is_backoffice_user
    return False


class BackofficeUserRequiredMixin(UserPassesTestMixin):
    login_url = 'backoffice:login'

    def test_func(self) -> bool:
        return is_backoffice_user(self.request.user)


backoffice_user_required = user_passes_test(is_backoffice_user, login_url='backoffice:login')
