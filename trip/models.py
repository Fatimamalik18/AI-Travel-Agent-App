# With constraints like no negative value etc
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import date

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

    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # ✅ CONSTRAINT: traveller_count > 0
    traveller_count = models.IntegerField(
        validators=[MinValueValidator(1)]  # 1 se kam nahi ho sakta
    )

    # ✅ CONSTRAINT: budget_total > 0
    budget_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]  # 0 ya negative nahi
    )

    travel_style = models.CharField(
        max_length=10,
        choices=TravelStyle.choices
    )

    transport_preference = models.CharField(
        max_length=30,
        choices=TransportMode.choices,
        default=TransportMode.MIXED
    )

    itinerary_json = models.JSONField(default=dict)

    status = models.CharField(
        max_length=10,
        choices=TripStatus.choices,
        default=TripStatus.DRAFT
    )

    is_public = models.BooleanField(default=False)

    # ✅ Auto-calculate max_days (ab editable nahi)
    max_days = models.IntegerField(
        default=0,
        editable=False  # 👈 User manually edit nahi kar sakta
    )
    
    max_destinations = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1)]  # Kam se kam 1 destination
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # ✅ Database level constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(traveller_count__gte=1),
                name='traveller_count_positive'
            ),
            models.CheckConstraint(
                check=models.Q(budget_total__gt=0),
                name='budget_total_positive'
            ),
            models.CheckConstraint(
                check=models.Q(max_destinations__gte=1),
                name='max_destinations_positive'
            ),
        ]

    def clean(self):
        """Model-level validation"""
        errors = {}
        
        # ✅ Start date cannot be in past
        if self.start_date and self.start_date < date.today():
            errors['start_date'] = 'Start date cannot be in the past!'
        
        # ✅ End date must be after start date
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                errors['end_date'] = 'End date must be after start date!'
        
        # ✅ Auto-calculate max_days
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.max_days = delta.days + 1  # +1 because inclusive
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()  # Clean validation call karein
        super().save(*args, **kwargs)

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

    # ✅ CHANGE: JSON se CharField mein convert kiya (enum ke liye)
    preferred_transport_modes = models.CharField(
        max_length=30,
        choices=TransportMode.choices,
        default=TransportMode.MIXED,
        blank=True,
        null=True
    )

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Preferences for {self.trip.title}"


# =========================
# TRIP DESTINATION MODEL (Table 3.4b)
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
    
    destination = models.ForeignKey(
        "destination.Destination",
        on_delete=models.RESTRICT,
        related_name="trip_destinations"
    )

    # ✅ CONSTRAINT: order_index > 0
    order_index = models.IntegerField(
        validators=[MinValueValidator(1)]  # 0 ya negative nahi
    )

    arrival_date = models.DateField(blank=True, null=True)
    departure_date = models.DateField(blank=True, null=True)
    
    # ✅ CONSTRAINT: nights >= 0
    nights = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]  # Negative nahi ho sakta
    )

    # ✅ CONSTRAINT: route_distance >= 0
    route_distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)]  # 0 ya positive
    )

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order_index']
        unique_together = [['trip', 'order_index']]
        # ✅ Database constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(order_index__gte=1),
                name='order_index_positive'
            ),
            models.CheckConstraint(
                check=models.Q(nights__gte=0),
                name='nights_positive'
            ),
            models.CheckConstraint(
                check=models.Q(route_distance_km__gte=0),
                name='route_distance_positive'
            ),
        ]

    def clean(self):
        """Model-level validation"""
        errors = {}
        
        # ✅ Arrival and departure date validation
        if self.arrival_date and self.departure_date:
            if self.departure_date <= self.arrival_date:
                errors['departure_date'] = 'Departure date must be after arrival date!'
        
        # ✅ Auto-calculate nights
        if self.arrival_date and self.departure_date:
            delta = self.departure_date - self.arrival_date
            self.nights = delta.days
        
        # ✅ Trip date validation
        if self.arrival_date and self.trip.start_date:
            if self.arrival_date < self.trip.start_date:
                errors['arrival_date'] = f'Arrival cannot be before trip start date ({self.trip.start_date})!'
        
        if self.departure_date and self.trip.end_date:
            if self.departure_date > self.trip.end_date:
                errors['departure_date'] = f'Departure cannot be after trip end date ({self.trip.end_date})!'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_index}. {self.destination.city_name} ({self.trip.title})"


# =========================
# TRIP INTERESTS JUNCTION TABLE (Table 3.7)
# =========================
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
# SHARED TRIPS MODEL - SIMPLIFIED
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
# SHARED TRIP USERS JUNCTION TABLE - SIMPLIFIED
# =========================
class SharedTripUser(models.Model):
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
        unique_together = [['shared_trip', 'user']]
        indexes = [
            models.Index(fields=['shared_trip', 'user']),
        ]
    
    def __str__(self):
        return f"{self.shared_trip.trip.title} → {self.user.email}"
    

# ==============================================================
# USER TRIP MAPPING
# ==============================================================
class UserTripStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    DONE = "done", "Done"


class UserTrip(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_trips"
    )

    trip = models.ForeignKey(
        "trip.Trip",
        on_delete=models.CASCADE,
        related_name="user_trips"
    )

    status = models.CharField(
        max_length=10,
        choices=UserTripStatus.choices,
        default=UserTripStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_trips"
        ordering = ['-created_at']
        unique_together = [['user', 'trip']]

    def __str__(self):
        return f"User: {self.user.email} - Trip: {self.trip.title} - Status: {self.status}"


# ==============================================================
# REVIEWS
# ==============================================================
class Review(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    trip = models.ForeignKey(
        "trip.Trip",  
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    review = models.TextField()
    
    rating = models.IntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars",
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews"
        ordering = ['-created_at']
        unique_together = [['user', 'trip']]
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='rating_between_1_and_5'
            ),
        ]

    def __str__(self):
        return f"Review by {self.user.email} for {self.trip.title} - Rating: {self.rating}/5"