from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserPreferences


# =========================
# CUSTOM USER ADMIN
# =========================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),

        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),

        ('Additional Information', {
            'fields': ('avatar_file', 'language', 'is_verified')
        }),

        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),

        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'avatar_file',
                    'language',
                    'is_verified',
                    'password1',
                    'password2',
                ),
            },
        ),
    )

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_verified',
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_verified')


# =========================
# USER PREFERENCES ADMIN
# =========================
@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'home_city',
        'preferred_seat_class',
        'travel_style',
        'max_budget_per_trip',
    )

    search_fields = (
        'user__username',
        'home_city',
        'travel_style',
    )

    list_filter = (
        'preferred_seat_class',
        'travel_style',
    )