from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка пользователей."""
    list_display = (
        'id', 'login', 'first_name', 'last_name',
    )
    list_display_links = ('login',)
    list_filter = ('login',)
    search_fields = ('login',)
    ordering = ('login', 'first_name', 'last_name')
