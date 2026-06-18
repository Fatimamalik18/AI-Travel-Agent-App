from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import (
    Itinerary,
    ItineraryDay,
    Activity
)

from .serializers import (
    ItinerarySerializer,
    ItineraryDaySerializer,
    ActivitySerializer
)


# ==========================
# ITINERARY CRUD
# ==========================

class ItineraryViewSet(viewsets.ModelViewSet):

    queryset = Itinerary.objects.all().order_by("-created_at")
    serializer_class = ItinerarySerializer

    @action(detail=False, methods=["get"])
    def by_trip(self, request):

        trip_id = request.query_params.get("trip_id")

        if not trip_id:
            return Response(
                {"error": "trip_id required"},
                status=400
            )

        itinerary = Itinerary.objects.filter(
            trip_id=trip_id
        ).first()

        if not itinerary:
            return Response(
                {"error": "Itinerary not found"},
                status=404
            )

        serializer = self.get_serializer(itinerary)

        return Response(serializer.data)


# ==========================
# ITINERARY DAY CRUD
# ==========================

class ItineraryDayViewSet(viewsets.ModelViewSet):

    queryset = ItineraryDay.objects.all().order_by("day_number")
    serializer_class = ItineraryDaySerializer

    def get_queryset(self):

        queryset = super().get_queryset()

        itinerary_id = self.request.query_params.get(
            "itinerary_id"
        )

        if itinerary_id:
            queryset = queryset.filter(
                itinerary_id=itinerary_id
            )

        return queryset


# ==========================
# ACTIVITY CRUD
# ==========================

class ActivityViewSet(viewsets.ModelViewSet):

    queryset = Activity.objects.all().order_by("order_index")
    serializer_class = ActivitySerializer

    def get_queryset(self):

        queryset = super().get_queryset()

        day_id = self.request.query_params.get("day_id")

        if day_id:
            queryset = queryset.filter(day_id=day_id)

        return queryset