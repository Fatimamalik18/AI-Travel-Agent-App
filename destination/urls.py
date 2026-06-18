from django.urls import path
from . import views

app_name = 'destination'

urlpatterns = [

    # =========================
    # DESTINATIONS
    # =========================
    path('destinations/', views.DestinationListCreateView.as_view(), name='destination-list-create'),
    path('destinations/<uuid:pk>/', views.DestinationRetrieveUpdateDestroyView.as_view(), name='destination-detail'),

    # =========================
    # ATTRACTIONS
    # =========================
    path('destinations/<uuid:destination_pk>/attractions/', views.AttractionListCreateView.as_view(), name='attraction-list-create'),
    path('destinations/<uuid:destination_pk>/attractions/<uuid:pk>/', views.AttractionRetrieveUpdateDestroyView.as_view(), name='attraction-detail'),

    # =========================
    # RESTAURANTS
    # =========================
    path('destinations/<uuid:destination_pk>/restaurants/', views.RestaurantListCreateView.as_view(), name='restaurant-list-create'),
    path('destinations/<uuid:destination_pk>/restaurants/<uuid:pk>/', views.RestaurantRetrieveUpdateDestroyView.as_view(), name='restaurant-detail'),

    # =========================
    # HOTELS
    # =========================
    path('destinations/<uuid:destination_pk>/hotels/', views.HotelListCreateView.as_view(), name='hotel-list-create'),
    path('destinations/<uuid:destination_pk>/hotels/<uuid:pk>/', views.HotelRetrieveUpdateDestroyView.as_view(), name='hotel-detail'),

    # =========================
    # TRANSPORT
    # =========================
    path('destinations/<uuid:destination_pk>/transport/', views.TransportListCreateView.as_view(), name='transport-list-create'),
    path('destinations/<uuid:destination_pk>/transport/<uuid:pk>/', views.TransportRetrieveUpdateDestroyView.as_view(), name='transport-detail'),

    # =========================
    # COST BENCHMARKS
    # =========================
    path('destinations/<uuid:destination_pk>/cost-benchmarks/', views.CostBenchmarkListCreateView.as_view(), name='cost-benchmark-list-create'),
    path('destinations/<uuid:destination_pk>/cost-benchmarks/<uuid:pk>/', views.CostBenchmarkRetrieveUpdateDestroyView.as_view(), name='cost-benchmark-detail'),

    # =========================
    # INTERESTS
    # =========================
    path('interests/', views.InterestListCreateView.as_view(), name='interest-list-create'),
    path('interests/<uuid:pk>/', views.InterestRetrieveUpdateDestroyView.as_view(), name='interest-detail'),
]