from rest_framework import serializers
from .models import Itinerary, ItineraryDay, Activity


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = "__all__"


class ItineraryDaySerializer(serializers.ModelSerializer):

    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = ItineraryDay
        fields = "__all__"


class ItinerarySerializer(serializers.ModelSerializer):

    days = ItineraryDaySerializer(many=True, read_only=True)

    class Meta:
        model = Itinerary
        fields = "__all__"