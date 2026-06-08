import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


# =========================
# CUSTOM USER MODEL
# =========================
class CustomUser(AbstractUser):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # already exists in AbstractUser but safe override allowed
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)

    avatar_file = models.FileField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    class LanguageChoices(models.TextChoices):
        ENGLISH = "en", "English"
        URDU = "ur", "Urdu"
        ARABIC = "ar", "Arabic"

    language = models.CharField(
        max_length=10,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ENGLISH
    )

    is_verified = models.BooleanField(default=False)

    # NOTE: is_staff already exists in AbstractUser → no need to redefine strongly
    is_staff = models.BooleanField(default=False)


# =========================
# USER PREFERENCES MODEL
# =========================
class UserPreferences(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="preferences"
    )

    home_city = models.CharField(max_length=100)

    travel_interests = models.JSONField(default=list)

    preferred_transport_modes = models.JSONField(default=list)

    preferred_seat_class = models.CharField(max_length=30)

    food_preferences = models.TextField(blank=True)

    travel_style = models.CharField(max_length=20)

    default_group_size = models.IntegerField(default=1)

    max_budget_per_trip = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)