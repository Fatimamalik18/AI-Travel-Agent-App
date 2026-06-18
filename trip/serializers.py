# Everything correct but Shared trip ka issue ha is me.... Get....shared trip
# (Who created ni show ho raha) or shared with bi ni show ho raha

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *


# =========================
# TRIP PREFERENCES SERIALIZER
# =========================
class TripPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripPreferences
        fields = [
            'id', 'budget_type', 'dietary_restrictions',
            'mobility_requirements', 'preferred_transport_modes', 'notes'
        ]
        read_only_fields = ['id']


# =========================
# TRIP DESTINATION SERIALIZER
# =========================
class TripDestinationSerializer(serializers.ModelSerializer):
    destination_name = serializers.CharField(
        source='destination.city_name', read_only=True
    )
    destination_province = serializers.CharField(
        source='destination.province', read_only=True
    )

    class Meta:
        model = TripDestination
        fields = [
            'id', 'destination', 'destination_name', 'destination_province',
            'order_index', 'arrival_date', 'departure_date',
            'nights', 'route_distance_km', 'notes'
        ]
        read_only_fields = ['id']


# =========================
# TRIP INTEREST SERIALIZER
# =========================
class TripInterestSerializer(serializers.ModelSerializer):
    interest_name = serializers.CharField(
        source='interest.name', read_only=True
    )

    class Meta:
        model = TripInterest
        fields = ['id', 'interest', 'interest_name']
        read_only_fields = ['id']


# =========================
# TRIP LIST SERIALIZER (lightweight)
# =========================
class TripListSerializer(serializers.ModelSerializer):
    destination_count = serializers.IntegerField(
        source='trip_destinations.count', read_only=True
    )

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'start_date', 'end_date',
            'traveller_count', 'budget_total', 'travel_style',
            'transport_preference', 'status', 'is_public',
            'destination_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# =========================
# TRIP DETAIL SERIALIZER (full nested)
# =========================
class TripDetailSerializer(serializers.ModelSerializer):
    preferences = TripPreferencesSerializer(required=False)
    trip_destinations = TripDestinationSerializer(many=True, read_only=True)
    interests = TripInterestSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'start_date', 'end_date',
            'traveller_count', 'budget_total', 'travel_style',
            'transport_preference', 'itinerary_json', 'status',
            'is_public', 'max_days', 'max_destinations',
            'preferences', 'trip_destinations', 'interests',
            'created_at', 'updated_at'
        ]
        # read_only_fields = ['id', 'itinerary_json', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        preferences_data = validated_data.pop('preferences', None)
        trip = Trip.objects.create(**validated_data)
        if preferences_data:
            TripPreferences.objects.create(trip=trip, **preferences_data)
        return trip

    def update(self, instance, validated_data):
        preferences_data = validated_data.pop('preferences', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if preferences_data is not None:
            TripPreferences.objects.update_or_create(
                trip=instance, defaults=preferences_data
            )
        return instance


# =========================
# AI ITINERARY GENERATION SERIALIZER
# =========================
class GenerateItinerarySerializer(serializers.Serializer):
    trip_id = serializers.UUIDField()

    def validate_trip_id(self, value):
        if not Trip.objects.filter(id=value).exists():
            raise serializers.ValidationError("Trip not found.")
        return value

# =========================
# SHARED TRIP USER SERIALIZER - SIMPLE
# =========================
class SharedTripUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    user_email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')

    class Meta:
        model = SharedTripUser
        fields = ['user_id', 'user_email', 'username', 'shared_at']


# =========================
# SHARED TRIP SERIALIZER
# =========================
class SharedTripSerializer(serializers.ModelSerializer):
    trip_title = serializers.CharField(source='trip.title', read_only=True)
    trip_status = serializers.CharField(source='trip.status', read_only=True)
    shared_with_users = SharedTripUserSerializer(many=True, read_only=True)
    share_url = serializers.SerializerMethodField()
    
    # Who created details
    who_created_id = serializers.IntegerField(source='who_created.id', read_only=True, allow_null=True)
    who_created_email = serializers.EmailField(source='who_created.email', read_only=True, allow_null=True)
    who_created_username = serializers.CharField(source='who_created.username', read_only=True, allow_null=True)

    class Meta:
        model = SharedTrip
        fields = [
            'id', 'trip', 'trip_title', 'trip_status',
            'share_token', 'share_url', 'expires_at',
            'created_at', 'shared_with_users',
            'who_created_id', 'who_created_email', 'who_created_username'
        ]
        read_only_fields = ['id', 'share_token', 'created_at']

    def get_share_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/shared-trips/by_token/{obj.share_token}/')
        return f'/api/shared-trips/by_token/{obj.share_token}/'


# =========================
# CREATE SHARED TRIP SERIALIZER - SIMPLE
# =========================
class CreateSharedTripSerializer(serializers.Serializer):
    trip_id = serializers.UUIDField()
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    shared_with = serializers.IntegerField(required=False, allow_null=True)  # Single user ID

    def validate_trip_id(self, value):
        if not Trip.objects.filter(id=value).exists():
            raise serializers.ValidationError("Trip not found.")
        return value
    
    def validate_shared_with(self, value):
        if value:
            User = get_user_model()
            if not User.objects.filter(id=value).exists():
                raise serializers.ValidationError("User not found.")
        return value


# =========================
# ADD USER TO SHARED TRIP SERIALIZER - SIMPLE
# =========================
class AddSharedTripUserSerializer(serializers.Serializer):
    shared_with = serializers.IntegerField()  # Single user ID
    
    def validate_shared_with(self, value):
        User = get_user_model()
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found.")
        return value


# =========================
# UPDATE SHARED TRIP SERIALIZER - SIMPLE
# =========================
class UpdateSharedTripSerializer(serializers.Serializer):
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    add_user = serializers.UUIDField(required=False, allow_null=True)  # ✅ Changed to UUIDField
    remove_user = serializers.UUIDField(required=False, allow_null=True)  # ✅ Changed to UUIDField
    
    def validate_add_user(self, value):
        if value:
            User = get_user_model()
            if not User.objects.filter(id=value).exists():
                raise serializers.ValidationError("User not found.")
        return value
    
    def validate_remove_user(self, value):
        if value:
            User = get_user_model()
            if not User.objects.filter(id=value).exists():
                raise serializers.ValidationError("User not found.")
        return value


from rest_framework import serializers
from .models import UserTrip, Review


# ==============================================================
# USER TRIP SERIALIZER
# ==============================================================
class UserTripSerializer(serializers.ModelSerializer):
    # Read-only friendly fields (extra info, frontend ke liye useful)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    trip_title = serializers.CharField(source='trip.title', read_only=True)

    class Meta:
        model = UserTrip
        fields = [
            'id',
            'user',
            'user_email',
            'trip',
            'trip_title',
            'status',
            'created_at',
            'updated_at',
        ]
        # user ko request se set karenge (view mein), client se direct nahi lenge
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Same user + same trip dobara map na ho (unique_together already
        DB level pe hai, lekin yahan clean error message dene ke liye check
        kar rahe hain).
        """
        request = self.context.get('request')
        trip = attrs.get('trip')

        if request and trip:
            qs = UserTrip.objects.filter(user=request.user, trip=trip)
            # Update ke waqt current instance ko exclude karo
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Is trip ka mapping pehle se is user ke liye maujood hai."
                )
        return attrs


# ==============================================================
# REVIEW SERIALIZER
# ==============================================================
class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    trip_title = serializers.CharField(source='trip.title', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'user_email',
            'trip',
            'trip_title',
            'review',
            'rating',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating 1 se 5 ke beech honi chahiye.")
        return value

    def validate(self, attrs):
        """
        Ek user ek trip ko sirf ek baar review kar sake (unique_together
        already DB level pe hai, yahan friendly validation error de rahe hain).
        """
        request = self.context.get('request')
        trip = attrs.get('trip')

        if request and trip:
            qs = Review.objects.filter(user=request.user, trip=trip)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Aap is trip ko pehle hi review kar chuke hain."
                )
        return attrs