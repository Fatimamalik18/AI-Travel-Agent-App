from django.urls import path
from . import views

urlpatterns = [
    # Trips
    path('trips/', views.TripListCreateView.as_view(), name='trip-list-create'),
    path('trips/public/', views.TripPublicListView.as_view(), name='trip-public-list'),
    path('trips/<uuid:pk>/', views.TripRetrieveUpdateDestroyView.as_view(), name='trip-detail'),
    path('trips/<uuid:pk>/update_status/', views.TripUpdateStatusView.as_view(), name='trip-update-status'),
    path('trips/<uuid:pk>/generate_itinerary/', views.TripGenerateItineraryView.as_view(), name='trip-generate-itinerary'),

    # Trip Destinations
    path('trips/<uuid:trip_pk>/destinations/', views.TripDestinationListCreateView.as_view(), name='trip-destination-list-create'),
    path('trips/<uuid:trip_pk>/destinations/<uuid:pk>/', views.TripDestinationRetrieveUpdateDestroyView.as_view(), name='trip-destination-detail'),

    # Trip Interests
    path('trips/<uuid:trip_pk>/interests/', views.TripInterestListCreateView.as_view(), name='trip-interest-list-create'),
    path('trips/<uuid:trip_pk>/interests/<uuid:pk>/', views.TripInterestRetrieveUpdateDestroyView.as_view(), name='trip-interest-detail'),

    # Trip Preferences (OneToOne)
    path('trips/<uuid:trip_pk>/preferences/', views.TripPreferencesView.as_view(), name='trip-preferences'),

    # Shared Trips
    path('shared-trips/', views.SharedTripListCreateView.as_view(), name='shared-trip-list-create'),
    path('shared-trips/<uuid:pk>/', views.SharedTripRetrieveUpdateDestroyView.as_view(), name='shared-trip-detail'),
    path('shared-trips/token/<str:token>/', views.SharedTripByTokenView.as_view(), name='shared-trip-by-token'),

    # Shared Trip Users
    path('shared-trips/<uuid:shared_trip_pk>/users/', views.SharedTripUserListCreateView.as_view(), name='shared-trip-user-list-create'),
    path('shared-trips/<uuid:shared_trip_pk>/users/<int:user_pk>/', views.SharedTripUserDestroyView.as_view(), name='shared-trip-user-destroy'),

    # ---------------- USER TRIP ----------------
    path('user-trips/', views.UserTripListCreateView.as_view(), name='usertrip-list-create'),
    path('user-trips/<uuid:pk>/', views.UserTripDetailView.as_view(), name='usertrip-detail'),

    # # ---------------- REVIEW ----------------
    path('reviews/',views.ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<uuid:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
]
