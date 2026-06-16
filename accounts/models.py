import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    first_name  = models.CharField(max_length=150, blank=True, null=True)
    last_name   = models.CharField(max_length=150, blank=True, null=True)
    avatar_file = models.FileField(upload_to="avatars/", blank=True, null=True)

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

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email or self.username


class UserPreferences(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="preferences"
    )

    class TravelInterestChoices(models.TextChoices):
        ADVENTURE = "adventure", "Adventure"
        CULTURE   = "culture", "Culture"
        NATURE    = "nature", "Nature"
        FOOD      = "food", "Food"
        SPORTS    = "sports", "Sports"

    travel_interests = models.CharField(
        max_length=20,
        choices=TravelInterestChoices.choices,
        blank=True
    )

    class TransportModeChoices(models.TextChoices):
        BUS    = "bus", "Bus"
        TRAIN  = "train", "Train"
        CAR    = "car", "Car"
        PLANE  = "plane", "Plane"

    preferred_transport_modes = models.CharField(
        max_length=20,
        choices=TransportModeChoices.choices,
        blank=True
    )

    class SeatClassChoices(models.TextChoices):
        ECONOMY     = "economy", "Economy"
        BUSINESS    = "business", "Business"
        FIRST_CLASS = "first", "First Class"

    preferred_seat_class = models.CharField(
        max_length=20,
        choices=SeatClassChoices.choices,
        blank=True
    )

    class FoodPreferenceChoices(models.TextChoices):
        VEG     = "veg", "Vegetarian"
        NON_VEG = "nonveg", "Non-Vegetarian"
        VEGAN   = "vegan", "Vegan"
        HALAL   = "halal", "Halal"

    food_preferences = models.CharField(
        max_length=20,
        choices=FoodPreferenceChoices.choices,
        blank=True
    )

    class TravelStyleChoices(models.TextChoices):
        SOLO    = "solo", "Solo"
        FAMILY  = "family", "Family"
        COUPLE  = "couple", "Couple"
        GROUP   = "group", "Group"

    travel_style = models.CharField(
        max_length=20,
        choices=TravelStyleChoices.choices,
        blank=True
    )

    default_group_size        = models.IntegerField(default=1)
    max_budget_per_trip       = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_preferences"

    def __str__(self):
        return f"{self.user.username} - Preferences"


# ===========================
# CHANGED: Interest ENUM ADDED
# ===========================
class Interest(models.Model):

    class InterestChoices(models.TextChoices):
        ADVENTURE = "adventure", "Adventure"
        CULTURE   = "culture", "Culture"
        NATURE    = "nature", "Nature"
        FOOD      = "food", "Food"
        SPORTS    = "sports", "Sports"
        TECH      = "tech", "Technology"
        MUSIC     = "music", "Music"
       

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # CHANGED: name field converted to ENUM
    name = models.CharField(
        max_length=20,
        choices=InterestChoices.choices,
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "interests"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SocialAccount(models.Model):
    class ProviderChoices(models.TextChoices):
        GOOGLE   = "google",   "Google"
        APPLE    = "apple",    "Apple"
        FACEBOOK = "facebook", "Facebook"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="social_accounts")

    provider = models.CharField(max_length=50, choices=ProviderChoices.choices)
    provider_user_id = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_accounts"
        unique_together = ("user", "provider")


class UserVehicle(models.Model):
    class FuelTypeChoices(models.TextChoices):
        PETROL   = "petrol", "Petrol"
        DIESEL   = "diesel", "Diesel"
        CNG      = "cng", "CNG"
        ELECTRIC = "electric", "Electric"
        HYBRID   = "hybrid", "Hybrid"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="vehicles")

    vehicle_name = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=30, choices=FuelTypeChoices.choices)
    avg_mileage_kmpl = models.DecimalField(max_digits=6, decimal_places=2)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Notification(models.Model):
    class NotificationTypeChoices(models.TextChoices):
        REMINDER = "reminder", "Reminder"
        ALERT    = "alert", "Alert"
        SYSTEM   = "system", "System"
    class NotificationStatusChoices(models.TextChoices):
        UNREAD = "unread", "Unread"
        READ   = "read", "Read"
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")

    type = models.CharField(max_length=30, choices=NotificationTypeChoices.choices)
    title = models.CharField(max_length=255)
    body = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=NotificationStatusChoices.choices, default=NotificationStatusChoices.UNREAD)   
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]