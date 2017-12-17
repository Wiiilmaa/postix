from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username: str, password: str=None, **kwargs):
        user = self.model(username=username, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username: str, password: str=None, **kwargs):
        if password is None:  # noqa
            raise Exception("You must provide a password")
        user = self.model(username=username, **kwargs)
        user.is_superuser = True
        user.is_troubleshooter = True
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser):

    username = models.CharField(max_length=254, unique=True)
    firstname = models.CharField(max_length=254, blank=True)
    lastname = models.CharField(max_length=254, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_backoffice_user = models.BooleanField(default=False)
    is_troubleshooter = models.BooleanField(default=False)
    auth_token = models.CharField(max_length=254, null=True, blank=True, unique=True)

    USERNAME_FIELD = EMAIL_FIELD = 'username'
    objects = UserManager()

    def has_perm(self, perm, obj=None) -> bool:  # noqa
        # Only for django.contrib.admin
        return self.is_superuser

    def has_module_perms(self, app_label) -> bool:  # noqa
        # Only for django.contrib.admin
        return self.is_superuser

    def get_short_name(self) -> str:  # noqa
        return self.username

    def get_full_name(self) -> str:  # noqa
        if self.firstname and self.lastname:
            return '{} {}'.format(self.firstname, self.lastname)
        elif self.firstname:
            return self.firstname
        return self.username

    @property
    def is_staff(self) -> bool:
        return self.is_superuser or self.is_backoffice_user or self.is_troubleshooter

    def get_current_session(self):
        from .cashdesk import CashdeskSession

        return CashdeskSession.objects.filter(user=self, end__isnull=True) \
            .order_by('-start').first()

    def __str__(self) -> str:
        return self.username
