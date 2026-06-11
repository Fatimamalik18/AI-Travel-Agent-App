from django.contrib import admin
from .models import Itinerary, ItineraryDay, Activity


# =========================
# ITINERARY ADMIN
# =========================
@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):

    list_display = (
        "trip_id",
        "estimated_total_cost",
        "accommodation_cost",
        "transport_cost",
        "food_cost",
        "activities_cost",
        "fuel_cost",
        "misc_cost",
        "created_at",
    )

    search_fields = ("trip_id",)

    readonly_fields = ("created_at",)


# =========================
# ITINERARY DAY ADMIN
# =========================
@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):

    list_display = (
        "itinerary",
        "day_number",
        "date",
        "theme",
    )

    list_filter = ("date",)

    search_fields = (
        "itinerary__trip_id",
        "theme",
    )

    ordering = ("day_number",)


# =========================
# ACTIVITY ADMIN
# =========================
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "day",
        "category",
        "transport_mode",
        "estimated_cost",
        "time",
        "order_index",
    )

    list_filter = (
        "category",
        "transport_mode",
    )

    search_fields = (
        "title",
        "description",
    )

    ordering = ("order_index",)