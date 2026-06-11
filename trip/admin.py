from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import (
    Trip, TripPreferences, TripDestination, TripInterest,
    SharedTrip, Itinerary, ItineraryDay, Activity
)


# =========================
# INLINE CLASSES
# =========================
class TripDestinationInline(admin.TabularInline):
    model = TripDestination
    extra = 1
    fields = ['destination', 'order_index', 'arrival_date', 'departure_date', 'nights', 'route_distance_km']
    autocomplete_fields = ['destination']


class TripInterestInline(admin.TabularInline):
    model = TripInterest
    extra = 1
    autocomplete_fields = ['interest']


class ItineraryDayInline(admin.TabularInline):
    model = ItineraryDay
    extra = 1
    fields = ['day_number', 'date', 'theme', 'trip_destination']
    show_change_link = True


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 1
    fields = ['order_index', 'time', 'title', 'category', 'estimated_cost']


# =========================
# TRIP ADMIN
# =========================
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'start_date', 'end_date', 'traveller_count',
        'budget_total', 'travel_style', 'status', 'created_at'
    ]

    list_filter = [
        'travel_style',
        'transport_preference',
        'status',
        'is_public',
        'created_at'
    ]

    search_fields = [
        'title',
        'user__username',
        'user__email'
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'status', 'is_public')
        }),
        ('Dates & Travelers', {
            'fields': ('start_date', 'end_date', 'traveller_count')
        }),
        ('Budget & Style', {
            'fields': ('budget_total', 'travel_style', 'transport_preference')
        }),
        ('AI Data', {
            'fields': ('itinerary_json',),
            'classes': ('collapse',)
        }),
        ('Limits', {
            'fields': ('max_days', 'max_destinations'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [TripDestinationInline, TripInterestInline]

    raw_id_fields = ['user']

    date_hierarchy = 'created_at'


# =========================
# TRIP PREFERENCES ADMIN
# =========================
@admin.register(TripPreferences)
class TripPreferencesAdmin(admin.ModelAdmin):
    list_display = ['trip_link', 'budget_type', 'dietary_restrictions_short']

    search_fields = ['trip__title', 'trip__user__username']

    list_filter = ['budget_type']

    raw_id_fields = ['trip']

    def trip_link(self, obj):
        url = reverse('admin:trip_trip_change', args=[obj.trip.id])
        return format_html('<a href="{}">{}</a>', url, obj.trip.title)

    trip_link.short_description = 'Trip'

    def dietary_restrictions_short(self, obj):
        return obj.dietary_restrictions[:50] if obj.dietary_restrictions else '-'

    dietary_restrictions_short.short_description = 'Dietary Restrictions'


# =========================
# TRIP DESTINATION ADMIN
# =========================
@admin.register(TripDestination)
class TripDestinationAdmin(admin.ModelAdmin):
    list_display = [
        'trip_link', 'destination_link', 'order_index',
        'arrival_date', 'departure_date', 'nights', 'route_distance_km'
    ]

    list_filter = ['trip__status']

    search_fields = [
        'trip__title',
        'destination__city_name'
    ]

    raw_id_fields = ['trip', 'destination']

    def trip_link(self, obj):
        url = reverse('admin:trip_trip_change', args=[obj.trip.id])
        return format_html('<a href="{}">{}</a>', url, obj.trip.title)

    trip_link.short_description = 'Trip'

    def destination_link(self, obj):
        url = reverse('admin:destination_destination_change', args=[obj.destination.id])
        return format_html('<a href="{}">{}</a>', url, obj.destination.city_name)

    destination_link.short_description = 'Destination'


# =========================
# SHARED TRIP ADMIN
# =========================
@admin.register(SharedTrip)
class SharedTripAdmin(admin.ModelAdmin):
    list_display = ['trip_link', 'share_token_short', 'who_created', 'expires_at', 'created_at']

    search_fields = ['trip__title', 'share_token']

    list_filter = ['expires_at']

    raw_id_fields = ['trip', 'who_created']

    readonly_fields = ['share_token', 'created_at']

    def trip_link(self, obj):
        url = reverse('admin:trip_trip_change', args=[obj.trip.id])
        return format_html('<a href="{}">{}</a>', url, obj.trip.title)

    trip_link.short_description = 'Trip'

    def share_token_short(self, obj):
        return obj.share_token[:16] + '...' if len(obj.share_token) > 16 else obj.share_token

    share_token_short.short_description = 'Token'


# =========================
# ITINERARY ADMIN (Inline view)
# =========================
@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = [
        'trip_link', 'estimated_total_cost', 'accommodation_cost',
        'transport_cost', 'food_cost', 'activities_cost', 'fuel_cost'
    ]

    readonly_fields = ['created_at']

    fieldsets = (
        ('Trip', {
            'fields': ('trip',)
        }),
        ('Cost Breakdown (PKR)', {
            'fields': (
                'estimated_total_cost',
                'accommodation_cost',
                'transport_cost',
                'food_cost',
                'activities_cost',
                'fuel_cost',
                'misc_cost'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    raw_id_fields = ['trip']
    inlines = [ItineraryDayInline]

    def trip_link(self, obj):
        url = reverse('admin:trip_trip_change', args=[obj.trip.id])
        return format_html('<a href="{}">{}</a>', url, obj.trip.title)

    trip_link.short_description = 'Trip'


# =========================
# ITINERARY DAY ADMIN
# =========================
@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    list_display = ['itinerary_link', 'day_number', 'date', 'theme', 'trip_destination_link']

    list_filter = ['itinerary__trip__status']

    search_fields = ['itinerary__trip__title', 'theme']

    raw_id_fields = ['itinerary', 'trip_destination']
    inlines = [ActivityInline]

    def itinerary_link(self, obj):
        return format_html(
            '<a href="{}">Itinerary for {}</a>',
            reverse('admin:trip_itinerary_change', args=[obj.itinerary.id]),
            obj.itinerary.trip.title
        )

    itinerary_link.short_description = 'Itinerary'

    def trip_destination_link(self, obj):
        if obj.trip_destination:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:trip_tripdestination_change', args=[obj.trip_destination.id]),
                obj.trip_destination.destination.city_name
            )
        return '-'

    trip_destination_link.short_description = 'Destination'


# =========================
# ACTIVITY ADMIN
# =========================
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'day_link', 'order_index', 'time', 'category',
        'transport_mode', 'estimated_cost'
    ]

    list_filter = ['category', 'transport_mode']

    search_fields = ['title', 'description', 'tips']

    raw_id_fields = ['day']

    fieldsets = (
        ('Activity Details', {
            'fields': ('day', 'title', 'description', 'tips')
        }),
        ('Schedule & Cost', {
            'fields': ('order_index', 'time', 'estimated_cost')
        }),
        ('Categorization', {
            'fields': ('category', 'transport_mode')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        })
    )

    def day_link(self, obj):
        return format_html(
            '<a href="{}">Day {} - {}</a>',
            reverse('admin:trip_itineraryday_change', args=[obj.day.id]),
            obj.day.day_number,
            obj.day.date
        )

    day_link.short_description = 'Day'