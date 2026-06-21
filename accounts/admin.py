from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    UserPreferences,
    SocialAccount,
    UserVehicle,
    Interest,
    Notification,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (None, {
            "fields": ("username", "password")
        }),
        ("Personal Info", {
            "fields": ("first_name", "last_name", "email", "avatar_file", "home_city")
        }),
        ("Settings", {
            "fields": ("language", "is_verified")
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Important Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email",
                "first_name", "last_name",
                "avatar_file", "home_city",
                "language", "is_verified",
                "password1", "password2",
            ),
        }),
    )

    list_display  = ("username", "email", "first_name", "last_name", "is_verified", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter   = ("is_staff", "is_verified", "language")
    ordering      = ("-date_joined",)


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):

    list_display  = ("user", "travel_style", "preferred_seat_class", "default_group_size", "max_budget_per_trip")
    search_fields = ("user__username", "user__email", "travel_style")
    list_filter   = ("travel_style", "preferred_seat_class")
    ordering      = ("user__username",)
    readonly_fields = ("id", "created_at", "updated_at")

    # ✅ CHECK ADDED: selected_interests ke liye multi-select widget (dono taraf list, ek se zyada select hosake)
    filter_horizontal = ("selected_interests",)


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):

    list_display  = ("user", "provider", "provider_user_id", "token_expires_at", "created_at")
    search_fields = ("user__username", "user__email", "provider_user_id")
    list_filter   = ("provider",)
    ordering      = ("-created_at",)
    readonly_fields = ("id", "created_at")


@admin.register(UserVehicle)
class UserVehicleAdmin(admin.ModelAdmin):

    list_display  = ("vehicle_name", "user", "fuel_type", "avg_mileage_kmpl", "is_default", "created_at")
    search_fields = ("vehicle_name", "user__username", "user__email")
    list_filter   = ("fuel_type", "is_default")
    ordering      = ("user__username", "vehicle_name")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):

    list_display  = ("name", "created_at")
    search_fields = ("name",)
    ordering      = ("name",)
    readonly_fields = ("id", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display  = ("title", "user", "type", "read_at", "created_at")
    search_fields = ("title", "body", "user__username", "user__email")
    list_filter   = ("type",)
    ordering      = ("-created_at",)
    readonly_fields = ("id", "created_at")