from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin


def troubleshooter_user(user):
    return user.is_troubleshooter


class TroubleshooterUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return troubleshooter_user(self.request.user)


troubleshooter_user_required = user_passes_test(troubleshooter_user, login_url='troubleshooter:login')
