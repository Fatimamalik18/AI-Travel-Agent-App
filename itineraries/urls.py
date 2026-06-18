from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ItineraryViewSet,
    ItineraryDayViewSet,
    ActivityViewSet
)

router = DefaultRouter()

router.register(
    r'itineraries',
    ItineraryViewSet,
    basename='itinerary'
)

router.register(
    r'itinerary-days',
    ItineraryDayViewSet,
    basename='itinerary-day'
)

router.register(
    r'activities',
    ActivityViewSet,
    basename='activity'
)

urlpatterns = [
    path('', include(router.urls)),
]