import uuid
from django.db import models
from accounts.models import CustomUser


# =========================
# ITINERARY
# =========================
class Itinerary(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    trip_id = models.UUIDField(unique=True)

    estimated_total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    accommodation_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    food_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activities_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fuel_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    misc_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "itineraries"

    def __str__(self):
        return f"Itinerary {self.trip_id}"


# =========================
# ITINERARY DAY
# =========================
class ItineraryDay(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name="days"
    )

    trip_destination_id = models.UUIDField(null=True, blank=True)

    day_number = models.IntegerField()
    date = models.DateField()

    theme = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "itinerary_days"
        ordering = ["day_number"]

    def __str__(self):
        return f"Day {self.day_number}"


# =========================
# ACTIVITY
# =========================
class Activity(models.Model):

    class ActivityCategory(models.TextChoices):
        FOOD = "food", "Food"
        ACTIVITY = "activity", "Activity"
        HOTEL = "hotel", "Hotel"
        TRANSPORT = "transport", "Transport"

    class TransportMode(models.TextChoices):
        CAR = "car", "Car"
        BUS = "bus", "Bus"
        WALK = "walk", "Walk"
        BIKE = "bike", "Bike"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    day = models.ForeignKey(
        ItineraryDay,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    order_index = models.IntegerField(default=1)
    time = models.TimeField(null=True, blank=True)

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    category = models.CharField(max_length=50, choices=ActivityCategory.choices)

    transport_mode = models.CharField(
        max_length=30,
        choices=TransportMode.choices,
        null=True,
        blank=True
    )

    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    tips = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activities"
        ordering = ["order_index"]
        unique_together = ("day", "title")

    def __str__(self):
        return self.title