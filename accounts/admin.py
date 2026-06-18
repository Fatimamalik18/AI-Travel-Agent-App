from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# ==============================================================
# CUSTOM BASE ADMIN CLASS (Sirf yahan ek baar filter lagega)
# ==============================================================
class UserSpecificAdmin(admin.ModelAdmin):
    """
    Ye base class automatically filter karegi data based on logged-in user.
    - Superuser ko sab data dikhega
    - Normal user ko sirf apna data dikhega
    """
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Agar superuser hai to sab dikhao
        if request.user.is_superuser:
            return qs
        
        # Normal user ko sirf apna data dikhao
        # Check karo ke model mein 'user' field hai ya nahi
        if hasattr(self.model, 'user'):
            return qs.filter(user=request.user)
        
        return qs
    
    def save_model(self, request, obj, form, change):
        """Jab naya object create ho to automatically user set kar do"""
        if not change and hasattr(obj, 'user'):
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        """User sirf apne objects edit kar sakta hai"""
        if not obj or request.user.is_superuser:
            return super().has_change_permission(request, obj)
        return obj.user == request.user
    
    def has_delete_permission(self, request, obj=None):
        """User sirf apne objects delete kar sakta hai"""
        if not obj or request.user.is_superuser:
            return super().has_delete_permission(request, obj)
        return obj.user == request.user


# ==============================================================
# CUSTOM USER ADMIN (User model ke liye alag se)
# ==============================================================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # User model mein 'user' field nahi hoti, isliye alag se handle karo
    
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
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Normal user sirf khud ko dekh sakta hai
        return qs.filter(id=request.user.id)


# ==============================================================
# USER PREFERENCES ADMIN (Base class inherit karega)
# ==============================================================
@admin.register(UserPreferences)
class UserPreferencesAdmin(UserSpecificAdmin):
    list_display  = ("user", "travel_style", "preferred_seat_class", "default_group_size", "max_budget_per_trip")
    search_fields = ("user__username", "user__email", "travel_style")
    list_filter   = ("travel_style", "preferred_seat_class")
    ordering      = ("user__username",)
    readonly_fields = ("id", "created_at", "updated_at")
    
    # Optional: user field ko readonly karo
    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        if obj:  # Existing object
            fields.append('user')
        return fields


# ==============================================================
# SOCIAL ACCOUNT ADMIN
# ==============================================================
@admin.register(SocialAccount)
class SocialAccountAdmin(UserSpecificAdmin):
    list_display  = ("user", "provider", "provider_user_id", "token_expires_at", "created_at")
    search_fields = ("user__username", "user__email", "provider_user_id")
    list_filter   = ("provider",)
    ordering      = ("-created_at",)
    readonly_fields = ("id", "created_at")


# ==============================================================
# USER VEHICLE ADMIN
# ==============================================================
@admin.register(UserVehicle)
class UserVehicleAdmin(UserSpecificAdmin):
    list_display  = ("vehicle_name", "user", "fuel_type", "avg_mileage_kmpl", "is_default", "created_at")
    search_fields = ("vehicle_name", "user__username", "user__email")
    list_filter   = ("fuel_type", "is_default")
    ordering      = ("user__username", "vehicle_name")
    readonly_fields = ("id", "created_at", "updated_at")


# ==============================================================
# INTEREST ADMIN (Interest ka user foreign key nahi hai)
# Interest global hai - sab user dekh sakte hain
# ==============================================================
@admin.register(UserInterest)
class InterestAdmin(admin.ModelAdmin):
    # Interest mein 'user' field nahi hai, isliye base class nahi use karenge
    list_display  = ("name", "created_at")
    search_fields = ("name",)
    ordering      = ("name",)
    readonly_fields = ("id", "created_at")
    
    # Interests global hone chahiye, isliye superuser ko bhi sirf sab dikhega
    def get_queryset(self, request):
        return super().get_queryset(request)


# ==============================================================
# NOTIFICATION ADMIN
# ==============================================================
@admin.register(Notification)
class NotificationAdmin(UserSpecificAdmin):
    list_display  = ("title", "user", "type", "read_at", "created_at")
    search_fields = ("title", "body", "user__username", "user__email")
    list_filter   = ("type",)
    ordering      = ("-created_at",)
    readonly_fields = ("id", "created_at")

