from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from .models import Itinerary, ItineraryDay, Activity
from django.utils import timezone


# =========================
# ITINERARY DAY FORM — Date check
# =========================
class ItineraryDayForm(forms.ModelForm):
    class Meta:
        model = ItineraryDay
        fields = "__all__"

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date and date < timezone.now().date():
            raise ValidationError("Purani date accept nahi hogi. Aaj ya future ki date dalein.")
        return date


# =========================
# ITINERARY FORM — Negative cost check
# =========================
class ItineraryForm(forms.ModelForm):
    class Meta:
        model = Itinerary
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        cost_fields = [
            "estimated_total_cost", "accommodation_cost", "transport_cost",
            "food_cost", "activities_cost", "fuel_cost", "misc_cost"
        ]
        for field in cost_fields:
            value = cleaned_data.get(field)
            if value is not None and value < 0:
                self.add_error(field, "Cost negative nahi ho sakti.")
        return cleaned_data


# =========================
# ACTIVITY INLINE
# =========================
class ActivityInline(admin.TabularInline):
    model   = Activity
    extra   = 0
    fields  = ("order_index", "time", "title", "category", "transport_mode", "estimated_cost")
    ordering = ("order_index",)


# =========================
# ITINERARY DAY INLINE
# =========================
class ItineraryDayInline(admin.TabularInline):
    model  = ItineraryDay
    form   = ItineraryDayForm   # ✅ date check yahan bhi lagega
    extra  = 0
    fields = ("day_number", "date", "theme")
    ordering = ("day_number",)


# =========================
# ITINERARY ADMIN
# =========================
@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    form = ItineraryForm            # ✅ negative cost check

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

    search_fields   = ("trip_id",)
    readonly_fields = ("id", "created_at")
    inlines         = [ItineraryDayInline]  # ✅ days directly itinerary ke andar dikhenge


# =========================
# ITINERARY DAY ADMIN
# =========================
@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    form = ItineraryDayForm         # ✅ date check

    list_display = (
        "itinerary",
        "day_number",
        "date",
        "theme",
    )

    list_filter     = ("date",)
    search_fields   = ("itinerary__trip_id", "theme")
    ordering        = ("day_number",)
    readonly_fields = ("id",)
    inlines         = [ActivityInline]  # ✅ activities directly day ke andar dikhenge


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

    list_filter     = ("category", "transport_mode")
    search_fields   = ("title", "description")
    ordering        = ("order_index",)
    readonly_fields = ("id", "created_at")