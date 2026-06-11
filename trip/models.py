import uuid
from django.db import models
from django.conf import settings


# =========================
# CHOICES (as per document Section 2.3)
# =========================
class TravelStyle(models.TextChoices):
    BUDGET = "budget", "Budget"
    COMFORT = "comfort", "Comfort"
    LUXURY = "luxury", "Luxury"


class TransportMode(models.TextChoices):
    FLIGHT = "flight", "Flight"
    TRAIN = "train", "Train"
    BUS = "bus", "Bus"
    PRIVATE = "private", "Private Vehicle"
    TAXI = "taxi", "Taxi/Ride-hailing"
    METRO = "metro", "Metro/Public Transport"
    MIXED = "mixed", "Mixed"


class TripStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SAVED = "saved", "Saved"
    SHARED = "shared", "Shared"
    COMPLETED = "completed", "Completed"


# =========================
# TRIP MODEL (Table 3.4)
# =========================
class Trip(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trips"
    )

    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    traveller_count = models.IntegerField()

    budget_total = models.DecimalField(max_digits=12, decimal_places=2)

    travel_style = models.CharField(
        max_length=10,
        choices=TravelStyle.choices
    )

    transport_preference = models.CharField(
        max_length=30,
        choices=TransportMode.choices,
        default=TransportMode.MIXED
    )

    itinerary_json = models.JSONField()

    status = models.CharField(
        max_length=10,
        choices=TripStatus.choices,
        default=TripStatus.DRAFT
    )

    is_public = models.BooleanField(default=False)

    max_days = models.IntegerField(default=14)
    max_destinations = models.IntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"


# =========================
# TRIP PREFERENCES MODEL (Table 3.5)
# =========================
class TripPreferences(models.Model):
    class BudgetType(models.TextChoices):
        TOTAL = "total", "Total Budget"
        PER_PERSON = "per_person", "Per Person"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    trip = models.OneToOneField(
        Trip,
        on_delete=models.CASCADE,
        related_name="preferences"
    )

    budget_type = models.CharField(
        max_length=10,
        choices=BudgetType.choices,
        default=BudgetType.TOTAL
    )

    dietary_restrictions = models.TextField(blank=True, null=True)
    mobility_requirements = models.TextField(blank=True, null=True)

    preferred_transport_modes = models.JSONField(default=list, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Preferences for {self.trip.title}"


# =========================
# DESTINATION MODEL (referenced from destinations app)
# We'll use a string reference to avoid circular import
# =========================
class Destination(models.Model):
    """
    This model is defined in the destination app.
    Including this as a proxy for reference in TripDestination.
    The actual model should be in destination/models.py
    """
    pass


# =========================
# TRIP DESTINATIONS MODEL (Table 3.4b)
# =========================
class TripDestination(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="trip_destinations"
    )

    # Using string reference to avoid circular import
    destination = models.ForeignKey(
        "destination.Destination",
        on_delete=models.RESTRICT,
        related_name="trip_destinations"
    )

    order_index = models.IntegerField()

    arrival_date = models.DateField(blank=True, null=True)
    departure_date = models.DateField(blank=True, null=True)
    nights = models.IntegerField(default=0)

    route_distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order_index']
        unique_together = [['trip', 'order_index']]

    def __str__(self):
        return f"{self.order_index}. {self.destination.city_name} ({self.trip.title})"


# =========================
# TRIP INTERESTS JUNCTION TABLE (Table 3.7)
# =========================
class Interest(models.Model):
    """
    This model is defined in the destination app.
    Including this as a proxy for reference in TripInterest.
    The actual model should be in destination/models.py
    """
    pass


class TripInterest(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="interests"
    )

    # Using string reference to avoid circular import
    interest = models.ForeignKey(
        "destination.Interest",
        on_delete=models.CASCADE,
        related_name="trips"
    )

    class Meta:
        unique_together = [['trip', 'interest']]

    def __str__(self):
        return f"{self.trip.title} - {self.interest.name}"


# =========================
# SHARED TRIPS MODEL (Table 3.11) - CORRECTED
# =========================
class SharedTrip(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    trip = models.OneToOneField(
        Trip,
        on_delete=models.CASCADE,
        related_name="shared_link"
    )

    who_created = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_shared_trips"
    )

    share_token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shared: {self.trip.title} (Token: {self.share_token[:8]}...)"


# =========================
# SHARED TRIP USERS JUNCTION TABLE (Many-to-Many with metadata)
# =========================
class SharedTripUser(models.Model):
    """
    Junction table to track which users a trip is shared with.
    Uses composite key of (shared_trip, user)
    """
    shared_trip = models.ForeignKey(
        SharedTrip,
        on_delete=models.CASCADE,
        related_name="shared_with_users"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shared_trips_received"
    )
    
    shared_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Composite primary key using unique_together
        unique_together = [['shared_trip', 'user']]
        indexes = [
            models.Index(fields=['shared_trip', 'user']),
        ]
    
    def __str__(self):
        return f"Trip '{self.shared_trip.trip.title}' shared with {self.user.email}"

# =========================
# ITINERARY MODEL (Table 3.8)
# =========================
class Itinerary(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    trip = models.OneToOneField(
        Trip,
        on_delete=models.CASCADE,
        related_name="itinerary"
    )

    estimated_total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    accommodation_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    food_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activities_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fuel_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    misc_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Itinerary for {self.trip.title}"


# =========================
# ITINERARY DAYS MODEL (Table 3.9)
# =========================
class ItineraryDay(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name="days"
    )

    trip_destination = models.ForeignKey(
        TripDestination,
        on_delete=models.CASCADE,
        related_name="itinerary_days",
        null=True,
        blank=True
    )

    day_number = models.IntegerField()
    date = models.DateField()
    theme = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['day_number']
        unique_together = [['itinerary', 'day_number']]

    def __str__(self):
        return f"Day {self.day_number}: {self.date}"


# =========================
# ACTIVITIES MODEL (Table 3.10)
# =========================
class ActivityCategory(models.TextChoices):
    FOOD = "food", "Food & Dining"
    ACTIVITY = "activity", "Activity"
    HOTEL = "hotel", "Hotel/Accommodation"
    TRANSPORT = "transport", "Transport"


class Activity(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    day = models.ForeignKey(
        ItineraryDay,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    order_index = models.IntegerField(default=1)
    time = models.TimeField(blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    category = models.CharField(
        max_length=50,
        choices=ActivityCategory.choices
    )

    transport_mode = models.CharField(
        max_length=30,
        choices=TransportMode.choices,
        blank=True,
        null=True
    )

    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)

    tips = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order_index']
        unique_together = [['day', 'title']]

    def save(self, *args, **kwargs):
        self.title = self.title.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"