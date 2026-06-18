
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# =========================
# CHOICES
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


class AttractionCategory(models.TextChoices):
    MUSEUM = "Museum", "Museum"
    PARK = "Park", "Park"
    HISTORICAL = "Historical", "Historical"
    RELIGIOUS = "Religious", "Religious"
    ADVENTURE = "Adventure", "Adventure"
    SHOPPING = "Shopping", "Shopping"


class RestaurantCategory(models.TextChoices):
    LOCAL = "Local", "Local Cuisine"
    FAST_FOOD = "Fast Food", "Fast Food"
    FINE_DINING = "Fine Dining", "Fine Dining"
    STREET_FOOD = "Street Food", "Street Food"
    CAFE = "Cafe", "Cafe"


class CuisineType(models.TextChoices):
    PAKISTANI = "Pakistani", "Pakistani"
    CHINESE = "Chinese", "Chinese"
    CONTINENTAL = "Continental", "Continental"
    FAST_FOOD = "Fast Food", "Fast Food"
    BBQ = "BBQ", "BBQ"
    SEA_FOOD = "Sea Food", "Sea Food"


class AccommodationType(models.TextChoices):
    BUDGET = "budget", "Budget"
    COMFORT = "comfort", "Comfort"
    LUXURY = "luxury", "Luxury"


# =========================
# DESTINATION MODEL
# =========================
class Destination(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    city_name = models.CharField(max_length=100)
    province = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    best_visiting_season = models.CharField(max_length=100, blank=True, null=True)

    # ✅ Budget constraints: 0 ya positive
    avg_budget_low = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0)]
    )
    avg_budget_mid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0)]
    )
    avg_budget_high = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0)]
    )

    popular_categories = models.JSONField(default=list, blank=True, null=True)

    # ✅ Latitude/Longitude constraints
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['city_name']
        # ✅ Database constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(avg_budget_low__gte=0) | models.Q(avg_budget_low__isnull=True),
                name='avg_budget_low_positive'
            ),
            models.CheckConstraint(
                check=models.Q(avg_budget_mid__gte=0) | models.Q(avg_budget_mid__isnull=True),
                name='avg_budget_mid_positive'
            ),
            models.CheckConstraint(
                check=models.Q(avg_budget_high__gte=0) | models.Q(avg_budget_high__isnull=True),
                name='avg_budget_high_positive'
            ),
        ]

    def clean(self):
        """Model-level validation"""
        errors = {}
        
        # ✅ Budget hierarchy validation (low <= mid <= high)
        if self.avg_budget_low and self.avg_budget_mid:
            if self.avg_budget_low > self.avg_budget_mid:
                errors['avg_budget_low'] = 'Low budget cannot be greater than mid budget!'
        
        if self.avg_budget_mid and self.avg_budget_high:
            if self.avg_budget_mid > self.avg_budget_high:
                errors['avg_budget_mid'] = 'Mid budget cannot be greater than high budget!'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.city_name}, {self.province}" if self.province else self.city_name


# =========================
# INTERESTS MODEL
# =========================
class Interest(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# ATTRACTIONS MODEL
# =========================
class Attraction(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="attractions"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    category = models.CharField(
        max_length=50,
        choices=AttractionCategory.choices
    )

    # ✅ entry_fee: 0 ya positive
    entry_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0.0)]
    )
    
    # ✅ duration_hours: 0 ya positive
    duration_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0)]
    )

    # ✅ Latitude/Longitude constraints
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['destination__city_name', 'name']
        unique_together = [['destination', 'name']]
        # ✅ Database constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(entry_fee__gte=0),
                name='attraction_entry_fee_positive'
            ),
            models.CheckConstraint(
                check=models.Q(duration_hours__gte=0) | models.Q(duration_hours__isnull=True),
                name='attraction_duration_positive'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.destination.city_name})"


# =========================
# RESTAURANT RECOMMENDATIONS MODEL
# =========================
class Restaurant(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="restaurants"
    )

    name = models.CharField(max_length=255)
    area = models.CharField(max_length=100)

    category = models.CharField(
        max_length=50,
        choices=RestaurantCategory.choices
    )

    cuisine_type = models.CharField(
        max_length=50,
        choices=CuisineType.choices,
        blank=True,
        null=True
    )

    # ✅ avg_cost_per_person: 0 ya positive
    avg_cost_per_person = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    
    # ✅ rating: 0-5
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['destination__city_name', '-rating', 'name']
        # ✅ Database constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(avg_cost_per_person__gte=0),
                name='restaurant_cost_positive'
            ),
            models.CheckConstraint(
                check=models.Q(rating__gte=0) & models.Q(rating__lte=5) | models.Q(rating__isnull=True),
                name='restaurant_rating_range'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.destination.city_name})"


# =========================
# HOTEL RECOMMENDATIONS MODEL
# =========================
class HotelRecommendation(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="hotels"
    )

    hotel_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    # ✅ rating: 0-5
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )

    accommodation_type = models.CharField(
        max_length=10,
        choices=AccommodationType.choices
    )

    # ✅ avg_price_low: 0 ya positive
    avg_price_low = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    
    # ✅ avg_price_high: 0 ya positive
    avg_price_high = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['destination__city_name', 'accommodation_type', 'hotel_name']
        # ✅ Database constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(avg_price_low__gte=0),
                name='hotel_price_low_positive'
            ),
            models.CheckConstraint(
                check=models.Q(avg_price_high__gte=0),
                name='hotel_price_high_positive'
            ),
            models.CheckConstraint(
                check=models.Q(rating__gte=0) & models.Q(rating__lte=5) | models.Q(rating__isnull=True),
                name='hotel_rating_range'
            ),
        ]

    def clean(self):
        """Model-level validation"""
        errors = {}
        
        # ✅ Price hierarchy validation (low <= high)
        if self.avg_price_low and self.avg_price_high:
            if self.avg_price_low > self.avg_price_high:
                errors['avg_price_low'] = 'Low price cannot be greater than high price!'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hotel_name} ({self.destination.city_name})"


# =========================
# TRANSPORT RECOMMENDATIONS MODEL
# =========================
class TransportRecommendation(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="transport_options"
    )

    transport_type = models.CharField(
        max_length=30,
        choices=TransportMode.choices
    )

    provider = models.CharField(max_length=100)
    origin = models.CharField(max_length=100)

    # ✅ estimated_cost: 0 ya positive
    estimated_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['destination__city_name', 'transport_type', 'estimated_cost']
        # ✅ Database constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(estimated_cost__gte=0),
                name='transport_cost_positive'
            ),
        ]

    def __str__(self):
        return f"{self.transport_type} from {self.origin} to {self.destination.city_name} via {self.provider}"


# =========================
# COST BENCHMARKS MODEL
# =========================
class CostBenchmark(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="cost_benchmarks"
    )

    travel_style = models.CharField(
        max_length=20,
        choices=TravelStyle.choices
    )

    # ✅ All costs: 0 ya positive
    avg_hotel_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    avg_food_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    avg_transport_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    avg_activity_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )

    # ✅ fuel_price: 0 ya positive
    fuel_price_per_litre = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0)]
    )

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['destination', 'travel_style']]
        # ✅ Database constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(avg_hotel_per_night__gte=0),
                name='benchmark_hotel_positive'
            ),
            models.CheckConstraint(
                check=models.Q(avg_food_per_day__gte=0),
                name='benchmark_food_positive'
            ),
            models.CheckConstraint(
                check=models.Q(avg_transport_per_day__gte=0),
                name='benchmark_transport_positive'
            ),
            models.CheckConstraint(
                check=models.Q(avg_activity_per_day__gte=0),
                name='benchmark_activity_positive'
            ),
            models.CheckConstraint(
                check=models.Q(fuel_price_per_litre__gte=0) | models.Q(fuel_price_per_litre__isnull=True),
                name='benchmark_fuel_positive'
            ),
        ]

    def __str__(self):
        return f"{self.destination.city_name} - {self.travel_style}"