from rest_framework import serializers
from .models import (
    Destination, Interest, Attraction, Restaurant,
    HotelRecommendation, TransportRecommendation, CostBenchmark
)


# =========================
# INTEREST SERIALIZER
# =========================
class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


# =========================
# ATTRACTION SERIALIZER
# =========================
class AttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = [
            'id', 'name', 'description', 'category',
            'entry_fee', 'duration_hours',
            'latitude', 'longitude', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# =========================
# RESTAURANT SERIALIZER
# =========================
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'area', 'category', 'cuisine_type',
            'avg_cost_per_person', 'rating', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# =========================
# HOTEL SERIALIZER
# =========================
class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelRecommendation
        fields = [
            'id', 'hotel_name', 'location', 'rating',
            'accommodation_type', 'avg_price_low', 'avg_price_high',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# =========================
# TRANSPORT SERIALIZER
# =========================
class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportRecommendation
        fields = [
            'id', 'transport_type', 'provider', 'origin',
            'estimated_cost', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# =========================
# COST BENCHMARK SERIALIZER
# =========================
class CostBenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostBenchmark
        fields = [
            'id', 'travel_style',
            'avg_hotel_per_night', 'avg_food_per_day',
            'avg_transport_per_day', 'avg_activity_per_day',
            'fuel_price_per_litre', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']


# =========================
# DESTINATION LIST SERIALIZER (lightweight)
# =========================
class DestinationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = [
            'id', 'city_name', 'province',
            'best_visiting_season', 'avg_budget_low',
            'avg_budget_mid', 'avg_budget_high',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# =========================
# DESTINATION DETAIL SERIALIZER (full nested)
# =========================
class DestinationDetailSerializer(serializers.ModelSerializer):
    attractions = AttractionSerializer(many=True, read_only=True)
    restaurants = RestaurantSerializer(many=True, read_only=True)
    hotels = HotelSerializer(many=True, read_only=True)
    transport_options = TransportSerializer(many=True, read_only=True)
    cost_benchmarks = CostBenchmarkSerializer(many=True, read_only=True)

    class Meta:
        model = Destination
        fields = [
            'id', 'city_name', 'province', 'description',
            'best_visiting_season',
            'avg_budget_low', 'avg_budget_mid', 'avg_budget_high',
            'popular_categories', 'latitude', 'longitude',
            'is_active', 'created_at',
            'attractions', 'restaurants', 'hotels',
            'transport_options', 'cost_benchmarks'
        ]
        read_only_fields = ['id', 'created_at']