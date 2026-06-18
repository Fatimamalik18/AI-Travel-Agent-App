from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import (
    Destination, Interest, Attraction, Restaurant,
    HotelRecommendation, TransportRecommendation,
    CostBenchmark
)
from django.core.exceptions import ValidationError


# =========================
# INLINE CLASSES
# =========================
class AttractionInline(admin.TabularInline):
    model = Attraction
    extra = 1
    fields = ['name', 'category', 'entry_fee', 'duration_hours', 'is_active']
    
    # ✅ UI validation attributes
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        form.base_fields['entry_fee'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['duration_hours'].widget.attrs.update({
            'min': 0,
            'step': 0.5
        })
        return formset


class RestaurantInline(admin.TabularInline):
    model = Restaurant
    extra = 1
    fields = ['name', 'area', 'category', 'cuisine_type', 'avg_cost_per_person', 'rating']
    
    # ✅ UI validation attributes
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        form.base_fields['avg_cost_per_person'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['rating'].widget.attrs.update({
            'min': 0,
            'max': 5,
            'step': 0.1
        })
        return formset


class HotelInline(admin.TabularInline):
    model = HotelRecommendation
    extra = 1
    fields = ['hotel_name', 'location', 'accommodation_type', 'avg_price_low', 'avg_price_high']
    
    # ✅ UI validation attributes
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        form.base_fields['avg_price_low'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_price_high'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['rating'].widget.attrs.update({
            'min': 0,
            'max': 5,
            'step': 0.1
        })
        return formset


class TransportInline(admin.TabularInline):
    model = TransportRecommendation
    extra = 1
    fields = ['transport_type', 'provider', 'origin', 'estimated_cost']
    
    # ✅ UI validation attributes
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        form.base_fields['estimated_cost'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        return formset


class CostBenchmarkInline(admin.TabularInline):
    model = CostBenchmark
    extra = 1
    fields = ['travel_style', 'avg_hotel_per_night', 'avg_food_per_day', 'avg_transport_per_day', 'avg_activity_per_day']
    
    # ✅ UI validation attributes
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        form.base_fields['avg_hotel_per_night'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_food_per_day'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_transport_per_day'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_activity_per_day'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['fuel_price_per_litre'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        return formset


# =========================
# DESTINATION ADMIN
# =========================
@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = [
        'city_name', 'province', 'best_visiting_season', 'is_active', 'created_at'
    ]

    list_filter = ['province', 'is_active', 'created_at']

    search_fields = ['city_name', 'province', 'description']

    readonly_fields = ['created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('city_name', 'province', 'description', 'is_active')
        }),
        ('Travel Information', {
            'fields': ('best_visiting_season', 'popular_categories')
        }),
        ('Budget Estimates (PKR per day)', {
            'fields': ('avg_budget_low', 'avg_budget_mid', 'avg_budget_high')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    inlines = [
        AttractionInline, RestaurantInline, HotelInline,
        TransportInline, CostBenchmarkInline
    ]

    actions = ['activate_destinations', 'deactivate_destinations']
    
    # ✅ UI validation attributes
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        form.base_fields['avg_budget_low'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_budget_mid'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_budget_high'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['latitude'].widget.attrs.update({
            'min': -90,
            'max': 90,
            'step': 0.000001
        })
        form.base_fields['longitude'].widget.attrs.update({
            'min': -180,
            'max': 180,
            'step': 0.000001
        })
        
        return form

    def activate_destinations(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} destination(s) activated.")

    activate_destinations.short_description = "Activate selected destinations"

    def deactivate_destinations(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} destination(s) deactivated.")

    deactivate_destinations.short_description = "Deactivate selected destinations"


# =========================
# INTEREST ADMIN
# =========================
@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name', 'trips_count', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']

    def trips_count(self, obj):
        return obj.trips.count()

    trips_count.short_description = "Associated Trips"


# =========================
# ATTRACTION ADMIN
# =========================
@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'destination_link', 'category', 'entry_fee',
        'duration_hours', 'is_active'
    ]

    list_filter = ['category', 'is_active', 'destination__province']

    search_fields = ['name', 'description', 'destination__city_name']

    raw_id_fields = ['destination']

    fieldsets = (
        ('Basic Information', {
            'fields': ('destination', 'name', 'description', 'is_active')
        }),
        ('Category & Timing', {
            'fields': ('category', 'entry_fee', 'duration_hours')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        })
    )
    
    # ✅ UI validation attributes
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        form.base_fields['entry_fee'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['duration_hours'].widget.attrs.update({
            'min': 0,
            'step': 0.5
        })
        form.base_fields['latitude'].widget.attrs.update({
            'min': -90,
            'max': 90,
            'step': 0.000001
        })
        form.base_fields['longitude'].widget.attrs.update({
            'min': -180,
            'max': 180,
            'step': 0.000001
        })
        
        return form

    def destination_link(self, obj):
        url = reverse('admin:destination_destination_change', args=[obj.destination.id])
        return format_html('<a href="{}">{}</a>', url, obj.destination.city_name)

    destination_link.short_description = 'Destination'


# =========================
# RESTAURANT ADMIN
# =========================
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'destination_link', 'area', 'category',
        'cuisine_type', 'avg_cost_per_person', 'rating'
    ]

    list_filter = ['category', 'cuisine_type', 'destination__city_name', 'is_active']

    search_fields = ['name', 'area', 'destination__city_name']

    raw_id_fields = ['destination']
    
    # ✅ UI validation attributes
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        form.base_fields['avg_cost_per_person'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['rating'].widget.attrs.update({
            'min': 0,
            'max': 5,
            'step': 0.1
        })
        
        return form

    def destination_link(self, obj):
        url = reverse('admin:destination_destination_change', args=[obj.destination.id])
        return format_html('<a href="{}">{}</a>', url, obj.destination.city_name)

    destination_link.short_description = 'Destination'


# =========================
# HOTEL RECOMMENDATION ADMIN
# =========================
@admin.register(HotelRecommendation)
class HotelRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'hotel_name', 'destination_link', 'location', 'accommodation_type',
        'price_range', 'rating'
    ]

    list_filter = ['accommodation_type', 'destination__city_name', 'is_active']

    search_fields = ['hotel_name', 'location', 'destination__city_name']

    raw_id_fields = ['destination']
    
    # ✅ UI validation attributes
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        form.base_fields['avg_price_low'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_price_high'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['rating'].widget.attrs.update({
            'min': 0,
            'max': 5,
            'step': 0.1
        })
        
        return form

    def destination_link(self, obj):
        url = reverse('admin:destination_destination_change', args=[obj.destination.id])
        return format_html('<a href="{}">{}</a>', url, obj.destination.city_name)

    destination_link.short_description = 'Destination'

    def price_range(self, obj):
        return f"PKR {obj.avg_price_low} - {obj.avg_price_high}"

    price_range.short_description = 'Price per night (PKR)'


# =========================
# TRANSPORT RECOMMENDATION ADMIN
# =========================
@admin.register(TransportRecommendation)
class TransportRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'transport_type', 'provider', 'origin', 'destination_link',
        'estimated_cost'
    ]

    list_filter = ['transport_type', 'destination__city_name']

    search_fields = ['provider', 'origin', 'destination__city_name', 'notes']

    raw_id_fields = ['destination']
    
    # ✅ UI validation attributes
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        form.base_fields['estimated_cost'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        
        return form

    def destination_link(self, obj):
        url = reverse('admin:destination_destination_change', args=[obj.destination.id])
        return format_html('<a href="{}">{}</a>', url, obj.destination.city_name)

    destination_link.short_description = 'Destination'


# =========================
# COST BENCHMARK ADMIN
# =========================
@admin.register(CostBenchmark)
class CostBenchmarkAdmin(admin.ModelAdmin):
    list_display = [
        'destination_link', 'travel_style', 'avg_hotel_per_night',
        'avg_food_per_day', 'fuel_price_per_litre', 'last_updated'
    ]

    list_filter = ['travel_style', 'destination__province']

    search_fields = ['destination__city_name']

    raw_id_fields = ['destination']

    readonly_fields = ['last_updated']

    fieldsets = (
        ('Destination & Style', {
            'fields': ('destination', 'travel_style')
        }),
        ('Cost Breakdown (PKR)', {
            'fields': (
                'avg_hotel_per_night',
                'avg_food_per_day',
                'avg_transport_per_day',
                'avg_activity_per_day'
            )
        }),
        ('Fuel Price', {
            'fields': ('fuel_price_per_litre',)
        }),
        ('Last Updated', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        })
    )
    
    # ✅ UI validation attributes
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        form.base_fields['avg_hotel_per_night'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_food_per_day'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_transport_per_day'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['avg_activity_per_day'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        form.base_fields['fuel_price_per_litre'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        
        return form

    def destination_link(self, obj):
        url = reverse('admin:destination_destination_change', args=[obj.destination.id])
        return format_html('<a href="{}">{}</a>', url, obj.destination.city_name)

    destination_link.short_description = 'Destination'