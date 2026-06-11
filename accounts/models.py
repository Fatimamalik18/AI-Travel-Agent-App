import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


# ==============================================================
# CUSTOM USER MODEL
# ERD Relation: users ||--|| user_preferences  (One to One)
#               users ||--o{ social_accounts   (One to Many)
#               users ||--o{ user_vehicles     (One to Many)
#               users ||--o{ notifications     (One to Many)
# ==============================================================
class CustomUser(AbstractUser):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    first_name  = models.CharField(max_length=150, blank=True, null=True)
    last_name   = models.CharField(max_length=150, blank=True, null=True)
    avatar_file = models.FileField(upload_to="avatars/", blank=True, null=True)

    # home_city yahan hai — ERD ke mutabiq users table mein
    home_city = models.CharField(max_length=100, blank=True, null=True)

    class LanguageChoices(models.TextChoices):
        ENGLISH = "en", "English"
        URDU    = "ur", "Urdu"
        ARABIC  = "ar", "Arabic"

    language = models.CharField(
        max_length=10,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ENGLISH
    )

    is_verified = models.BooleanField(default=False)
    # is_staff AbstractUser mein already hai — dobara define nahi kiya

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email or self.username


# ==============================================================
# USER PREFERENCES MODEL
# OneToOneField — ek user ki sirf ek preferences row hogi
# ERD Relation: users ||--|| user_preferences
# home_city yahan se hata di — ab users table mein hai
# ==============================================================
class UserPreferences(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # OneToOneField — ForeignKey nahi, One to One relation hai
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="preferences"
    )

    travel_interests          = models.JSONField(default=list, blank=True)
    preferred_transport_modes = models.JSONField(default=list, blank=True)
    preferred_seat_class      = models.CharField(max_length=30, blank=True)
    food_preferences          = models.TextField(blank=True)
    travel_style              = models.CharField(max_length=20, blank=True)
    default_group_size        = models.IntegerField(default=1)
    max_budget_per_trip       = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_preferences"

    def __str__(self):
        return f"{self.user.username} - Preferences"


# ==============================================================
# SOCIAL ACCOUNT MODEL
# ERD Relation: users ||--o{ social_accounts  (One to Many)
# ==============================================================
class SocialAccount(models.Model):

    class ProviderChoices(models.TextChoices):
        GOOGLE   = "google",   "Google"
        APPLE    = "apple",    "Apple"
        FACEBOOK = "facebook", "Facebook"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="social_accounts"
    )

    provider         = models.CharField(max_length=50, choices=ProviderChoices.choices)
    provider_user_id = models.CharField(max_length=255)
    access_token     = models.TextField()
    refresh_token    = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_accounts"
        # Ek user ka ek provider pe sirf ek account
        unique_together = ("user", "provider")

    def __str__(self):
        return f"{self.user.username} - {self.provider}"


# ==============================================================
# USER VEHICLE MODEL
# ==============================================================
class UserVehicle(models.Model):

    class FuelTypeChoices(models.TextChoices):
        PETROL   = "petrol",   "Petrol"
        DIESEL   = "diesel",   "Diesel"
        CNG      = "cng",      "CNG"
        ELECTRIC = "electric", "Electric"
        HYBRID   = "hybrid",   "Hybrid"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="vehicles"
    )

    vehicle_name     = models.CharField(max_length=100)
    fuel_type        = models.CharField(max_length=30, choices=FuelTypeChoices.choices)
    avg_mileage_kmpl = models.DecimalField(max_digits=6, decimal_places=2)
    is_default       = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_vehicles"

    def __str__(self):
        return f"{self.user.username} - {self.vehicle_name}"


# ==============================================================
# INTEREST MODEL
# ==============================================================
class Interest(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "interests"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==============================================================
# NOTIFICATION MODEL
# ==============================================================
class Notification(models.Model):

    class NotificationTypeChoices(models.TextChoices):
        REMINDER = "reminder", "Reminder"
        ALERT    = "alert",    "Alert"
        SYSTEM   = "system",   "System"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    type    = models.CharField(max_length=30, choices=NotificationTypeChoices.choices)
    title   = models.CharField(max_length=255)
    body    = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"