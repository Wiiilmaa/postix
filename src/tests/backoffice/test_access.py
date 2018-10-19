import pytest
from django.contrib.auth.models import AnonymousUser

from postix.backoffice.views.utils import is_backoffice_user, is_superuser

from ..factories import user_factory


@pytest.mark.django_db
def test_backoffice_user_access():
    assert is_backoffice_user(user_factory(backoffice=True))
    assert not is_backoffice_user(user_factory())
    assert is_backoffice_user(user_factory(superuser=True))
    assert not is_backoffice_user(AnonymousUser)

    assert is_superuser(user_factory(superuser=True))
    assert not is_superuser(user_factory())
    assert not is_superuser(AnonymousUser)
