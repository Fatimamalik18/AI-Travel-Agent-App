# -*- coding: utf-8 -*-
"""
seed_dummy_data.py
===================
Yeh management command project ke HAR table mein dummy/sample data
insert karta hai (sahi dependency order mein, taake foreign keys aur
model-level validations (clean/save) break na hon).

USAGE:
    python manage.py seed_dummy_data
    python manage.py seed_dummy_data --flush   # pehle purana dummy data delete kare ga

Apps covered:
    accounts    -> CustomUser, UserPreferences, Interest, SocialAccount,
                   UserVehicle, Notification
    destination -> Destination, Interest, Attraction, Restaurant,
                   HotelRecommendation, TransportRecommendation, CostBenchmark
    trip        -> Trip, TripPreferences, TripDestination, TripInterest,
                   SharedTrip, SharedTripUser, UserTrip, Review
    itineraries -> Itinerary, ItineraryDay, Activity
    AI_engine   -> LLMUsageLog, AIPromptResponseLog
"""

import random
import uuid
from decimal import Decimal
from datetime import timedelta, time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import (
    CustomUser,
    UserPreferences,
    Interest as AccountInterest,
    SocialAccount,
    UserVehicle,
    Notification,
)
from destination.models import (
    Destination,
    Interest as DestinationInterest,
    Attraction,
    Restaurant,
    HotelRecommendation,
    TransportRecommendation,
    CostBenchmark,
    AttractionCategory,
    RestaurantCategory,
    CuisineType,
    AccommodationType,
    TransportMode as DestTransportMode,
    TravelStyle as DestTravelStyle,
)
from trip.models import (
    Trip,
    TripPreferences,
    TripDestination,
    TripInterest,
    SharedTrip,
    SharedTripUser,
    UserTrip,
    Review,
    TravelStyle as TripTravelStyle,
    TransportMode as TripTransportMode,
    TripStatus,
)
from itineraries.models import Itinerary, ItineraryDay, Activity
from AI_engine.models import LLMUsageLog, AIPromptResponseLog


# ==========================================================
# SAMPLE / SEED DATA POOLS (Pakistan-focused, lekin generic)
# ==========================================================

FIRST_NAMES = [
    "Ahmed", "Ali", "Hassan", "Bilal", "Usman", "Hamza", "Zain", "Saad",
    "Ayesha", "Sara", "Fatima", "Hira", "Mahnoor", "Zara", "Mariam", "Iqra",
]
LAST_NAMES = [
    "Khan", "Ahmed", "Malik", "Raza", "Sheikh", "Iqbal", "Butt", "Qureshi",
    "Hussain", "Farooq",
]
CITIES_HOME = ["Islamabad", "Lahore", "Karachi", "Multan", "Peshawar", "Quetta", "Faisalabad"]

DESTINATIONS = [
    ("Hunza", "Gilgit-Baltistan", "Sar sabz waadi jahan buland pahar aur jhilein dil moh leti hain.", "May-September"),
    ("Skardu", "Gilgit-Baltistan", "Adventure lovers ke liye jannat, jhilon aur trekking trails se bharpoor.", "April-October"),
    ("Murree", "Punjab", "Pahaadi mausam aur thandi hawaon ke saath family trip ke liye behtareen.", "March-October"),
    ("Naran Kaghan", "Khyber Pakhtunkhwa", "Khoobsurat jhilein aur sar sabz maidan, monsoon mein bhi popular.", "June-September"),
    ("Swat", "Khyber Pakhtunkhwa", "Switzerland of the East kehlane wali waadi.", "April-October"),
    ("Lahore", "Punjab", "Tareekhi shehar, Mughal architecture aur lazeez khane ka markaz.", "October-March"),
    ("Karachi", "Sindh", "Sahil samandar aur shehar ki raunaq, business aur tafreeh dono.", "November-February"),
    ("Islamabad", "Islamabad Capital Territory", "Sukoon bhara paitakht shehar, Margalla Hills ke daman mein.", "October-April"),
    ("Fairy Meadows", "Gilgit-Baltistan", "Nanga Parbat ke neeche basi ek jannat numa jagah.", "June-September"),
    ("Gwadar", "Balochistan", "Sahil-e-samandar aur machli giri ke liye mash'hoor port city.", "November-February"),
]

ATTRACTION_NAMES = [
    "Old Fort", "Hill View Point", "City Museum", "Central Park",
    "Lakeview Trail", "Heritage Walk", "Botanical Garden", "Adventure Park",
    "Shopping Bazaar", "Sunset Point",
]

RESTAURANT_NAMES = [
    "Spice Route", "Karahi Corner", "The Grill House", "Cafe Mocha",
    "Street Food Hub", "Royal Dastarkhwan", "Tandoori Nights", "Pearl Continental Cafe",
]

HOTEL_NAMES = [
    "Pearl Continental", "Marriott", "Serena Hotel", "Hill View Resort",
    "Lakeside Inn", "Mountain Lodge", "City Comfort Inn", "Heritage Guest House",
]

VEHICLE_NAMES = ["Honda Civic", "Toyota Corolla", "Suzuki Alto", "Toyota Hilux", "Honda City"]

TRIP_TITLES = [
    "Northern Areas Adventure", "Family Trip to Murree", "Solo Backpacking in Hunza",
    "Lahore Heritage Tour", "Honeymoon in Skardu", "Friends Road Trip to Swat",
    "Karachi Beach Getaway", "Eid Trip to Naran",
]

NOTIFICATION_TITLES = [
    ("reminder", "Upcoming Trip Reminder", "Aapki trip 3 din baad shuru hone wali hai, packing complete karein."),
    ("alert", "Budget Alert", "Aapka trip budget 80% tak pohanch chuka hai."),
    ("system", "Profile Updated", "Aapki profile information successfully update ho gayi hai."),
]

LLM_MODELS = ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-7"]

REVIEW_TEXTS = [
    "Bohat zabardast trip thi, sab kuch plan ke mutabiq hua.",
    "Itinerary acha tha lekin transport thoda mehnga laga.",
    "Family ke saath behtareen experience, dobara zaroor jayenge.",
    "Hotel recommendations bohat acchi thi, staff bhi friendly tha.",
    "Budget ke hisaab se trip kaafi reasonable rahi.",
]


def rand_decimal(low, high, places=2):
    val = random.uniform(low, high)
    quant = Decimal("1").scaleb(-places)  # e.g. places=2 -> Decimal('0.01')
    return Decimal(str(val)).quantize(quant)


class Command(BaseCommand):
    help = "Har table mein dummy/sample data insert karta hai (development/testing ke liye)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Pehle is command se bana hua dummy data delete kar dein (email pattern 'dummyuser' walay users).",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=8,
            help="Kitne dummy users banane hain (default: 8)",
        )
        parser.add_argument(
            "--trips-per-user",
            type=int,
            default=2,
            help="Har user ke liye kitni trips banani hain (default: 2)",
        )

    def handle(self, *args, **options):
        random.seed()
        self.num_users = options["users"]
        self.trips_per_user = options["trips_per_user"]

        if options["flush"]:
            self._flush_dummy_data()

        with transaction.atomic():
            users = self._create_users()
            self._create_account_interests()
            self._create_user_preferences(users)
            self._create_social_accounts(users)
            self._create_user_vehicles(users)
            self._create_notifications(users)

            destinations = self._create_destinations()
            dest_interests = self._create_destination_interests()
            self._create_attractions(destinations)
            self._create_restaurants(destinations)
            self._create_hotels(destinations)
            self._create_transport_options(destinations)
            self._create_cost_benchmarks(destinations)

            trips = self._create_trips(users)
            self._create_trip_preferences(trips)
            self._create_trip_destinations(trips, destinations)
            self._create_trip_interests(trips, dest_interests)
            self._create_user_trips(users, trips)
            shared_trips = self._create_shared_trips(trips, users)
            self._create_shared_trip_users(shared_trips, users)
            self._create_reviews(users, trips)

            itineraries = self._create_itineraries(trips)
            days = self._create_itinerary_days(itineraries)
            self._create_activities(days)

            self._create_llm_usage_logs(users, trips)
            self._create_ai_prompt_logs(users, trips)

        self.stdout.write(self.style.SUCCESS("\n✅ Dummy data tamaam tables mein successfully insert ho gaya hai!"))

    # ------------------------------------------------------------
    # FLUSH (optional cleanup of previously seeded data)
    # ------------------------------------------------------------
    def _flush_dummy_data(self):
        self.stdout.write("Purana dummy data delete kiya ja raha hai...")

        # Trip model mein user ka direct FK nahi hai (sirf UserTrip junction
        # table ke zariye link hai), is liye pehle dummy users ki trips ko
        # UserTrip se dhoond kar explicitly delete karte hain — warna yeh
        # orphan reh jati hain aur dobara run par duplicate trips ban jati hain.
        dummy_user_ids = list(
            CustomUser.objects.filter(username__startswith="dummyuser").values_list("id", flat=True)
        )
        Trip.objects.filter(user_trips__user_id__in=dummy_user_ids).distinct().delete()

        # Ab users delete karte hain — CASCADE ki wajah se UserPreferences,
        # SocialAccount, UserVehicle, Notification, UserTrip, Review,
        # SharedTripUser waghera bhi khud-ba-khud delete ho jate hain.
        deleted_users, _ = CustomUser.objects.filter(username__startswith="dummyuser").delete()

        # Destinations ko qasdan delete NAHI kiya ja raha — yeh reusable
        # reference/lookup data hai aur Trip se RESTRICT FK ke zariye
        # protected hai. get_or_create() ki wajah se dobara seed run
        # karne par yeh duplicate bhi nahi banegi.
        self.stdout.write(self.style.WARNING(f"Purana dummy data delete ho gaya ({deleted_users} related rows).\n"))

    # ------------------------------------------------------------
    # ACCOUNTS APP
    # ------------------------------------------------------------
    def _create_users(self):
        self.stdout.write("→ Users (CustomUser) ban rahe hain...")
        users = []
        for i in range(self.num_users):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            username = f"dummyuser{i+1}"
            email = f"{username}@example.com"

            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults=dict(
                    email=email,
                    first_name=first,
                    last_name=last,
                    home_city=random.choice(CITIES_HOME),
                    language=random.choice(["en", "ur", "ar"]),
                    is_verified=random.choice([True, False]),
                ),
            )
            if created:
                user.set_password("DummyPass123!")
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"   {len(users)} users tayar."))
        return users

    def _create_account_interests(self):
        self.stdout.write("→ Account Interests ban rahe hain...")
        choices = [c[0] for c in AccountInterest.InterestChoices.choices]
        count = 0
        for choice in choices:
            _, created = AccountInterest.objects.get_or_create(name=choice)
            count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {len(choices)} interests confirm/ban gaye."))

    def _create_user_preferences(self, users):
        self.stdout.write("→ UserPreferences ban rahi hain...")
        created_count = 0
        for user in users:
            _, created = UserPreferences.objects.get_or_create(
                user=user,
                defaults=dict(
                    travel_interests=random.choice(UserPreferences.TravelInterestChoices.values),
                    preferred_transport_modes=random.choice(UserPreferences.TransportModeChoices.values),
                    preferred_seat_class=random.choice(UserPreferences.SeatClassChoices.values),
                    food_preferences=random.choice(UserPreferences.FoodPreferenceChoices.values),
                    travel_style=random.choice(UserPreferences.TravelStyleChoices.values),
                    default_group_size=random.randint(1, 6),
                    max_budget_per_trip=random.randint(20000, 500000),
                ),
            )
            created_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {created_count} preferences ban gayi."))

    def _create_social_accounts(self, users):
        self.stdout.write("→ SocialAccounts ban rahe hain...")
        created_count = 0
        # har user ke liye 1 random provider (unique_together user+provider hai)
        for user in users:
            if random.random() < 0.6:  # sab users ke social account nahi honge
                provider = random.choice(SocialAccount.ProviderChoices.values)
                _, created = SocialAccount.objects.get_or_create(
                    user=user,
                    provider=provider,
                    defaults=dict(
                        provider_user_id=str(uuid.uuid4())[:20],
                        access_token=str(uuid.uuid4()),
                        refresh_token=str(uuid.uuid4()),
                        token_expires_at=timezone.now() + timedelta(days=30),
                    ),
                )
                created_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {created_count} social accounts ban gaye."))

    def _create_user_vehicles(self, users):
        self.stdout.write("→ UserVehicles ban rahi hain...")
        created_count = 0
        for user in users:
            if random.random() < 0.5:
                UserVehicle.objects.create(
                    user=user,
                    vehicle_name=random.choice(VEHICLE_NAMES),
                    fuel_type=random.choice(UserVehicle.FuelTypeChoices.values),
                    avg_mileage_kmpl=rand_decimal(8, 22, 2),
                    is_default=True,
                )
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"   {created_count} vehicles ban gayi."))

    def _create_notifications(self, users):
        self.stdout.write("→ Notifications ban rahi hain...")
        created_count = 0
        for user in users:
            for _ in range(random.randint(1, 3)):
                ntype, title, body = random.choice(NOTIFICATION_TITLES)
                status = random.choice(Notification.NotificationStatusChoices.values)
                read_at = timezone.now() - timedelta(hours=random.randint(1, 48)) if status == "read" else None
                Notification.objects.create(
                    user=user,
                    type=ntype,
                    title=title,
                    body=body,
                    status=status,
                    read_at=read_at,
                )
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"   {created_count} notifications ban gayi."))

    # ------------------------------------------------------------
    # DESTINATION APP
    # ------------------------------------------------------------
    def _create_destinations(self):
        self.stdout.write("→ Destinations ban rahe hain...")
        destinations = []
        for city, province, desc, season in DESTINATIONS:
            low = rand_decimal(3000, 8000)
            mid = rand_decimal(float(low) + 1000, float(low) + 15000)
            high = rand_decimal(float(mid) + 1000, float(mid) + 30000)
            dest, created = Destination.objects.get_or_create(
                city_name=city,
                defaults=dict(
                    province=province,
                    description=desc,
                    best_visiting_season=season,
                    avg_budget_low=low,
                    avg_budget_mid=mid,
                    avg_budget_high=high,
                    popular_categories=random.sample(
                        [c[0] for c in AttractionCategory.choices], k=3
                    ),
                    latitude=rand_decimal(24.0, 37.0, 6),
                    longitude=rand_decimal(61.0, 77.0, 6),
                    is_active=True,
                ),
            )
            destinations.append(dest)
        self.stdout.write(self.style.SUCCESS(f"   {len(destinations)} destinations tayar."))
        return destinations

    def _create_destination_interests(self):
        self.stdout.write("→ Destination Interests ban rahe hain...")
        names = ["Adventure", "Culture", "Nature", "Food", "Sports", "Shopping", "History"]
        interests = []
        for name in names:
            obj, _ = DestinationInterest.objects.get_or_create(name=name)
            interests.append(obj)
        self.stdout.write(self.style.SUCCESS(f"   {len(interests)} destination interests tayar."))
        return interests

    def _create_attractions(self, destinations):
        self.stdout.write("→ Attractions ban rahi hain...")
        created_count = 0
        for dest in destinations:
            used_names = random.sample(ATTRACTION_NAMES, k=4)
            for name in used_names:
                full_name = f"{dest.city_name} {name}"
                _, created = Attraction.objects.get_or_create(
                    destination=dest,
                    name=full_name,
                    defaults=dict(
                        description=f"{full_name} ek mash'hoor jagah hai jo tourists ko bohat pasand aati hai.",
                        category=random.choice(AttractionCategory.values),
                        entry_fee=rand_decimal(0, 1500),
                        duration_hours=rand_decimal(1, 5, 1),
                        latitude=rand_decimal(24.0, 37.0, 6),
                        longitude=rand_decimal(61.0, 77.0, 6),
                        is_active=True,
                    ),
                )
                created_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {created_count} attractions ban gayi."))

    def _create_restaurants(self, destinations):
        self.stdout.write("→ Restaurants ban rahe hain...")
        created_count = 0
        for dest in destinations:
            for name in random.sample(RESTAURANT_NAMES, k=3):
                Restaurant.objects.create(
                    destination=dest,
                    name=f"{name} - {dest.city_name}",
                    area=f"{dest.city_name} Center",
                    category=random.choice(RestaurantCategory.values),
                    cuisine_type=random.choice(CuisineType.values),
                    avg_cost_per_person=rand_decimal(300, 5000),
                    rating=rand_decimal(2.5, 5.0, 1),
                    is_active=True,
                )
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"   {created_count} restaurants ban gaye."))

    def _create_hotels(self, destinations):
        self.stdout.write("→ Hotels ban rahe hain...")
        created_count = 0
        for dest in destinations:
            for name in random.sample(HOTEL_NAMES, k=3):
                low = rand_decimal(3000, 10000)
                high = rand_decimal(float(low) + 2000, float(low) + 40000)
                HotelRecommendation.objects.create(
                    destination=dest,
                    hotel_name=f"{name} {dest.city_name}",
                    location=f"{dest.city_name}, {dest.province or ''}".strip(", "),
                    rating=rand_decimal(2.5, 5.0, 1),
                    accommodation_type=random.choice(AccommodationType.values),
                    avg_price_low=low,
                    avg_price_high=high,
                    is_active=True,
                )
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"   {created_count} hotels ban gaye."))

    def _create_transport_options(self, destinations):
        self.stdout.write("→ Transport options ban rahe hain...")
        created_count = 0
        for dest in destinations:
            for origin in random.sample(CITIES_HOME, k=3):
                TransportRecommendation.objects.create(
                    destination=dest,
                    transport_type=random.choice(DestTransportMode.values),
                    provider=random.choice(["Daewoo", "PIA", "Faisal Movers", "Local Transport", "Careem"]),
                    origin=origin,
                    estimated_cost=rand_decimal(500, 25000),
                    notes="Booking advance mein karwana behtar hai.",
                )
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"   {created_count} transport options ban gaye."))

    def _create_cost_benchmarks(self, destinations):
        self.stdout.write("→ Cost Benchmarks ban rahe hain...")
        created_count = 0
        for dest in destinations:
            for style in DestTravelStyle.values:
                _, created = CostBenchmark.objects.get_or_create(
                    destination=dest,
                    travel_style=style,
                    defaults=dict(
                        avg_hotel_per_night=rand_decimal(2000, 30000),
                        avg_food_per_day=rand_decimal(500, 8000),
                        avg_transport_per_day=rand_decimal(300, 5000),
                        avg_activity_per_day=rand_decimal(200, 4000),
                        fuel_price_per_litre=rand_decimal(260, 290),
                    ),
                )
                created_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {created_count} cost benchmarks ban gaye."))

    # ------------------------------------------------------------
    # TRIP APP
    # ------------------------------------------------------------
    def _create_trips(self, users):
        self.stdout.write("→ Trips ban rahi hain...")
        trips = []
        for user in users:
            for _ in range(self.trips_per_user):
                start = timezone.now().date() + timedelta(days=random.randint(5, 90))
                end = start + timedelta(days=random.randint(2, 10))
                trip = Trip.objects.create(
                    title=random.choice(TRIP_TITLES),
                    start_date=start,
                    end_date=end,
                    traveller_count=random.randint(1, 6),
                    budget_total=rand_decimal(20000, 600000),
                    travel_style=random.choice(TripTravelStyle.values),
                    transport_preference=random.choice(TripTransportMode.values),
                    itinerary_json={"note": "dummy itinerary placeholder", "days": []},
                    status=random.choice(TripStatus.values),
                    is_public=random.choice([True, False]),
                    max_destinations=random.randint(1, 4),
                )
                trips.append((trip, user))
        self.stdout.write(self.style.SUCCESS(f"   {len(trips)} trips ban gayi."))
        return trips

    def _create_trip_preferences(self, trips):
        self.stdout.write("→ TripPreferences ban rahi hain...")
        created_count = 0
        for trip, _ in trips:
            _, created = TripPreferences.objects.get_or_create(
                trip=trip,
                defaults=dict(
                    budget_type=random.choice(TripPreferences.BudgetType.values),
                    dietary_restrictions=random.choice(["Halal only", "No restrictions", "Vegetarian preferred", ""]),
                    mobility_requirements=random.choice(["None", "Wheelchair accessible needed", ""]),
                    preferred_transport_modes=random.choice(TripTransportMode.values),
                    notes="Auto-generated dummy preference.",
                ),
            )
            created_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {created_count} trip preferences ban gayi."))

    def _create_trip_destinations(self, trips, destinations):
        self.stdout.write("→ TripDestinations ban rahi hain...")
        created_count = 0
        for trip, _ in trips:
            chosen = random.sample(destinations, k=min(trip.max_destinations, len(destinations)))
            current_date = trip.start_date
            for idx, dest in enumerate(chosen, start=1):
                nights = random.randint(1, 3)
                arrival = current_date
                departure = arrival + timedelta(days=nights)
                if departure > trip.end_date:
                    departure = trip.end_date
                if arrival >= departure:
                    continue
                TripDestination.objects.create(
                    trip=trip,
                    destination=dest,
                    order_index=idx,
                    arrival_date=arrival,
                    departure_date=departure,
                    route_distance_km=rand_decimal(20, 800),
                    notes=f"{dest.city_name} ka qayam.",
                )
                current_date = departure
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"   {created_count} trip destinations ban gayi."))

    def _create_trip_interests(self, trips, dest_interests):
        self.stdout.write("→ TripInterests ban rahi hain...")
        created_count = 0
        for trip, _ in trips:
            for interest in random.sample(dest_interests, k=min(2, len(dest_interests))):
                _, created = TripInterest.objects.get_or_create(trip=trip, interest=interest)
                created_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {created_count} trip interests ban gayi."))

    def _create_user_trips(self, users, trips):
        self.stdout.write("→ UserTrips ban rahi hain...")
        created_count = 0
        for trip, owner in trips:
            _, created = UserTrip.objects.get_or_create(
                user=owner,
                trip=trip,
                defaults=dict(status=random.choice(UserTrip._meta.get_field("status").choices)[0]),
            )
            created_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {created_count} user-trip mappings ban gayi."))

    def _create_shared_trips(self, trips, users):
        self.stdout.write("→ SharedTrips ban rahe hain...")
        shared_trips = []
        for trip, owner in trips:
            if random.random() < 0.4 and trip.is_public:
                shared, created = SharedTrip.objects.get_or_create(
                    trip=trip,
                    defaults=dict(
                        who_created=owner,
                        share_token=str(uuid.uuid4()),
                        expires_at=timezone.now() + timedelta(days=15),
                    ),
                )
                if created:
                    shared_trips.append(shared)
        self.stdout.write(self.style.SUCCESS(f"   {len(shared_trips)} shared trips ban gaye."))
        return shared_trips

    def _create_shared_trip_users(self, shared_trips, users):
        self.stdout.write("→ SharedTripUsers ban rahe hain...")
        created_count = 0
        for shared in shared_trips:
            others = [u for u in users if u.id != shared.who_created_id]
            for user in random.sample(others, k=min(2, len(others))):
                _, created = SharedTripUser.objects.get_or_create(shared_trip=shared, user=user)
                created_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {created_count} shared-trip-user records ban gaye."))

    def _create_reviews(self, users, trips):
        self.stdout.write("→ Reviews ban rahi hain...")
        created_count = 0
        for trip, owner in trips:
            if random.random() < 0.6:
                _, created = Review.objects.get_or_create(
                    user=owner,
                    trip=trip,
                    defaults=dict(
                        review=random.choice(REVIEW_TEXTS),
                        rating=random.randint(2, 5),
                    ),
                )
                created_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"   {created_count} reviews ban gayi."))

    # ------------------------------------------------------------
    # ITINERARIES APP
    # ------------------------------------------------------------
    def _create_itineraries(self, trips):
        self.stdout.write("→ Itineraries ban rahi hain...")
        itineraries = []
        for trip, _ in trips:
            acc = rand_decimal(5000, 50000)
            trans = rand_decimal(2000, 20000)
            food = rand_decimal(2000, 15000)
            act = rand_decimal(1000, 10000)
            fuel = rand_decimal(500, 5000)
            misc = rand_decimal(500, 5000)
            total = acc + trans + food + act + fuel + misc
            itinerary, created = Itinerary.objects.get_or_create(
                trip_id=trip.id,
                defaults=dict(
                    estimated_total_cost=total,
                    accommodation_cost=acc,
                    transport_cost=trans,
                    food_cost=food,
                    activities_cost=act,
                    fuel_cost=fuel,
                    misc_cost=misc,
                ),
            )
            if created:
                itineraries.append((itinerary, trip))
        self.stdout.write(self.style.SUCCESS(f"   {len(itineraries)} itineraries ban gayi."))
        return itineraries

    def _create_itinerary_days(self, itineraries):
        self.stdout.write("→ ItineraryDays ban rahe hain...")
        days = []
        for itinerary, trip in itineraries:
            trip_dest_ids = list(
                TripDestination.objects.filter(trip=trip).values_list("destination_id", "id")
            )
            num_days = max((trip.end_date - trip.start_date).days, 1)
            for day_num in range(1, num_days + 1):
                day_date = trip.start_date + timedelta(days=day_num - 1)
                # sirf future/aaj ki date set karein (validator ki wajah se)
                if day_date < timezone.now().date():
                    day_date = timezone.now().date() + timedelta(days=day_num)
                trip_dest_id = random.choice(trip_dest_ids)[1] if trip_dest_ids else None
                day = ItineraryDay.objects.create(
                    itinerary=itinerary,
                    trip_destination_id=None,  # FK nahi hai, sirf UUID reference field hai
                    day_number=day_num,
                    date=day_date,
                    theme=random.choice(
                        ["Sightseeing", "Relaxation", "Adventure", "Local Food Tour", "Travel Day"]
                    ),
                )
                days.append(day)
        self.stdout.write(self.style.SUCCESS(f"   {len(days)} itinerary days ban gaye."))
        return days

    def _create_activities(self, days):
        self.stdout.write("→ Activities ban rahi hain...")
        created_count = 0
        activity_titles = [
            "Breakfast at local cafe", "City sightseeing tour", "Hotel check-in",
            "Mountain hike", "Local market visit", "Dinner at restaurant",
            "Transport to next city", "Evening leisure walk",
        ]
        for day in days:
            used_titles = random.sample(activity_titles, k=min(3, len(activity_titles)))
            for idx, title in enumerate(used_titles, start=1):
                category = random.choice(Activity.ActivityCategory.values)
                Activity.objects.create(
                    day=day,
                    order_index=idx,
                    time=time(hour=random.randint(7, 20), minute=random.choice([0, 15, 30, 45])),
                    title=f"{title} (Day {day.day_number})",
                    description=f"{title} - dummy description for testing.",
                    category=category,
                    transport_mode=random.choice(Activity.TransportMode.values) if category == "transport" else None,
                    estimated_cost=rand_decimal(100, 5000),
                    latitude=rand_decimal(24.0, 37.0, 6),
                    longitude=rand_decimal(61.0, 77.0, 6),
                    tips="Advance planning behtar rahegi.",
                )
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"   {created_count} activities ban gayi."))

    # ------------------------------------------------------------
    # AI_ENGINE APP
    # ------------------------------------------------------------
    def _create_llm_usage_logs(self, users, trips):
        self.stdout.write("→ LLMUsageLogs ban rahe hain...")
        created_count = 0
        for trip, owner in trips:
            for _ in range(random.randint(1, 2)):
                input_tok = random.randint(200, 3000)
                output_tok = random.randint(100, 2000)
                LLMUsageLog.objects.create(
                    user=owner,
                    trip_id=trip.id,
                    model=random.choice(LLM_MODELS),
                    input_tokens=input_tok,
                    output_tokens=output_tok,
                    cost_usd=round((input_tok * 0.000003) + (output_tok * 0.000015), 6),
                    success=random.choice([True, True, True, False]),
                )
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"   {created_count} LLM usage logs ban gaye."))

    def _create_ai_prompt_logs(self, users, trips):
        self.stdout.write("→ AIPromptResponseLogs ban rahe hain...")
        created_count = 0
        sample_prompts = [
            "Mujhe 5 din ka Hunza trip plan bana kar dein.",
            "Lahore mein best food places suggest karein.",
            "Family ke liye budget-friendly itinerary banayein.",
        ]
        sample_responses = [
            "Yahan aapke liye 5-din ka detailed Hunza itinerary hai...",
            "Lahore ki kuch behtareen food spots yeh hain...",
            "Family-friendly budget itinerary tayar hai...",
        ]
        for trip, owner in trips:
            AIPromptResponseLog.objects.create(
                user=owner,
                trip_id=trip.id,
                prompt_text=random.choice(sample_prompts),
                response_text=random.choice(sample_responses),
                model=random.choice(LLM_MODELS),
                prompt_tokens=random.randint(50, 800),
                response_tokens=random.randint(100, 1500),
                latency_ms=random.randint(300, 4000),
                is_successful=True,
            )
            created_count += 1
        self.stdout.write(self.style.SUCCESS(f"   {created_count} AI prompt-response logs ban gaye."))
