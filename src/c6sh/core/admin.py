from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User


@admin.register(User)
class AuthorAdmin(BaseUserAdmin):
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('username', 'password', 'auth_token')}),
        ('Personal info', {'fields': ('firstname', 'lastname')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_troubleshooter')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'firstname', 'lastname', 'is_active', 'is_superuser', 'is_troubleshooter')
    list_filter = ('is_active', 'is_superuser', 'is_troubleshooter')
    search_fields = ('firstname', 'lastname', 'username')
    ordering = ('username',)
    filter_horizontal = []


admin.site.unregister(Group)
