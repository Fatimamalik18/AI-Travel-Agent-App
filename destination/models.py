import uuid
from django.db import models


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
# DESTINATION MODEL (Table 3.12)
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

    avg_budget_low = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    avg_budget_mid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    avg_budget_high = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    popular_categories = models.JSONField(default=list, blank=True, null=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['city_name']

    def __str__(self):
        return f"{self.city_name}, {self.province}" if self.province else self.city_name


# =========================
# INTERESTS MODEL (Table 3.6)
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
# ATTRACTIONS MODEL (Table 3.13)
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

    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['destination__city_name', 'name']
        unique_together = [['destination', 'name']]

    def __str__(self):
        return f"{self.name} ({self.destination.city_name})"


# =========================
# RESTAURANT RECOMMENDATIONS MODEL (Table 3.14)
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

    avg_cost_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['destination__city_name', '-rating', 'name']

    def __str__(self):
        return f"{self.name} ({self.destination.city_name})"


# =========================
# HOTEL RECOMMENDATIONS MODEL (Table 3.15)
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

    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    accommodation_type = models.CharField(
        max_length=10,
        choices=AccommodationType.choices
    )

    avg_price_low = models.DecimalField(max_digits=10, decimal_places=2)
    avg_price_high = models.DecimalField(max_digits=10, decimal_places=2)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['destination__city_name', 'accommodation_type', 'hotel_name']

    def __str__(self):
        return f"{self.hotel_name} ({self.destination.city_name})"


# =========================
# TRANSPORT RECOMMENDATIONS MODEL (Table 3.16)
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

    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['destination__city_name', 'transport_type', 'estimated_cost']

    def __str__(self):
        return f"{self.transport_type} from {self.origin} to {self.destination.city_name} via {self.provider}"


# =========================
# COST BENCHMARKS MODEL (Table 3.18)
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

    avg_hotel_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    avg_food_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    avg_transport_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    avg_activity_per_day = models.DecimalField(max_digits=10, decimal_places=2)

    fuel_price_per_litre = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['destination', 'travel_style']]

    def __str__(self):
        return f"{self.destination.city_name} - {self.travel_style}"

