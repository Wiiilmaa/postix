from django.contrib.auth.decorators import user_passes_test


def backoffice_user(user):
    return user.is_superuser


backoffice_user_required = user_passes_test(backoffice_user, login_url='backoffice:login')
