from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from .models import (
    Trip, TripPreferences, TripDestination, TripInterest,
    SharedTrip, SharedTripUser, UserTrip, Review
)
from django.core.exceptions import ValidationError

User = get_user_model()


# =========================
# INLINE CLASSES
# =========================
class TripDestinationInline(admin.TabularInline):
    model = TripDestination
    extra = 1
    fields = ['destination', 'order_index', 'arrival_date', 'departure_date', 'nights', 'route_distance_km']
    autocomplete_fields = ['destination']
    
    # ✅ UI validation - negative values nahi le sakte
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        
        # HTML5 validation attributes
        form.base_fields['order_index'].widget.attrs.update({
            'min': 1,
            'step': 1
        })
        form.base_fields['nights'].widget.attrs.update({
            'min': 0,
            'step': 1
        })
        form.base_fields['route_distance_km'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        return formset


class TripInterestInline(admin.TabularInline):
    model = TripInterest
    extra = 1
    autocomplete_fields = ['interest']


class SharedTripUserInline(admin.TabularInline):
    model = SharedTripUser
    extra = 1
    fields = ['user', 'shared_at']
    readonly_fields = ['shared_at']
    autocomplete_fields = ['user']
    raw_id_fields = ['user']


# =========================
# TRIP ADMIN
# =========================
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = [
        'title','start_date', 'end_date', 'traveller_count',
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
    ]

    readonly_fields = ['created_at', 'updated_at', 'max_days']  # ✅ max_days readonly

    fieldsets = (
        ('Basic Information', {
            'fields': ( 'title', 'status', 'is_public')
        }),
        ('Dates & Travelers', {
            'fields': ('start_date', 'end_date', 'traveller_count')
        }),
        ('Budget & Style', {
            'fields': ('budget_total', 'travel_style', 'transport_preference')
        }),
        ('Limits', {
            'fields': ('max_days', 'max_destinations'),  # ✅ max_days auto-calculated
            'classes': ('collapse',)
        }),
        ('AI Data', {
            'fields': ('itinerary_json',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [TripDestinationInline, TripInterestInline]
    date_hierarchy = 'created_at'
    
    # ✅ UI validation attributes
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        form.base_fields['traveller_count'].widget.attrs.update({
            'min': 1,
            'step': 1
        })
        form.base_fields['budget_total'].widget.attrs.update({
            'min': 0.01,
            'step': 0.01
        })
        form.base_fields['max_destinations'].widget.attrs.update({
            'min': 1,
            'step': 1
        })
        
        return form
    
    def save_model(self, request, obj, form, change):
        """Save karte waqt validation"""
        try:
            obj.full_clean()
        except ValidationError as e:
            self.message_user(request, f"Error: {e}", level='ERROR')
            return
        super().save_model(request, obj, form, change)


# =========================
# TRIP PREFERENCES ADMIN
# =========================
@admin.register(TripPreferences)
class TripPreferencesAdmin(admin.ModelAdmin):
    list_display = ['trip_link', 'budget_type', 'preferred_transport_modes', 'dietary_restrictions_short']

    search_fields = ['trip__title', 'dietary_restrictions']

    list_filter = ['budget_type', 'preferred_transport_modes']

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
    
    # ✅ UI validation attributes
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        form.base_fields['order_index'].widget.attrs.update({
            'min': 1,
            'step': 1
        })
        form.base_fields['nights'].widget.attrs.update({
            'min': 0,
            'step': 1
        })
        form.base_fields['route_distance_km'].widget.attrs.update({
            'min': 0,
            'step': 0.01
        })
        
        return form

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
    list_display = ['trip_link', 'share_token_short', 'who_created', 'shared_users_count', 'expires_at', 'created_at']
    
    search_fields = ['trip__title', 'share_token']
    
    list_filter = ['expires_at']
    
    raw_id_fields = ['trip', 'who_created']
    
    readonly_fields = ['share_token', 'created_at']
    
    inlines = [SharedTripUserInline]
    
    def trip_link(self, obj):
        url = reverse('admin:trip_trip_change', args=[obj.trip.id])
        return format_html('<a href="{}">{}</a>', url, obj.trip.title)
    
    trip_link.short_description = 'Trip'
    
    def share_token_short(self, obj):
        return obj.share_token[:16] + '...' if len(obj.share_token) > 16 else obj.share_token
    
    share_token_short.short_description = 'Token'
    
    def shared_users_count(self, obj):
        count = obj.shared_with_users.count()
        if count == 0:
            return '-'
        users = obj.shared_with_users.select_related('user')[:3]
        user_list = [su.user.email for su in users]
        display = ', '.join(user_list)
        if count > 3:
            display += f' (+{count - 3} more)'
        return display
    
    shared_users_count.short_description = 'Shared Users'


# =========================
# USER TRIP ADMIN
# =========================
@admin.register(UserTrip)
class UserTripAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'trip_link', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email', 'user__username', 'trip__title']
    raw_id_fields = ['user', 'trip']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    
    user_link.short_description = 'User'
    
    def trip_link(self, obj):
        url = reverse('admin:trip_trip_change', args=[obj.trip.id])
        return format_html('<a href="{}">{}</a>', url, obj.trip.title)
    
    trip_link.short_description = 'Trip'


# =========================
# REVIEW ADMIN
# =========================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'trip_link', 'rating', 'review_short', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__email', 'user__username', 'trip__title', 'review']
    raw_id_fields = ['user', 'trip']
    readonly_fields = ['created_at', 'updated_at']
    
    # ✅ UI validation
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['rating'].widget.attrs.update({
            'min': 1,
            'max': 5,
            'step': 1
        })
        return form
    
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    
    user_link.short_description = 'User'
    
    def trip_link(self, obj):
        url = reverse('admin:trip_trip_change', args=[obj.trip.id])
        return format_html('<a href="{}">{}</a>', url, obj.trip.title)
    
    trip_link.short_description = 'Trip'
    
    def review_short(self, obj):
        return obj.review[:50] + '...' if len(obj.review) > 50 else obj.review
    
    review_short.short_description = 'Review'