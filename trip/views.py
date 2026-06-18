import secrets
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .models import (
    Trip, TripDestination, TripInterest, TripPreferences,
    SharedTrip, SharedTripUser, TripStatus, UserTrip, Review
)
from .serializers import *

User = get_user_model()


# =========================
# TRIPS
# =========================

class TripListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Trip.objects.prefetch_related(
            'trip_destinations__destination',
            'interests__interest',
            'preferences'
        )

        trip_status = request.query_params.get('status')
        if trip_status:
            qs = qs.filter(status=trip_status)

        travel_style = request.query_params.get('travel_style')
        if travel_style:
            qs = qs.filter(travel_style=travel_style)

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(title__icontains=search)

        ordering = request.query_params.get('ordering', '-created_at')
        allowed_ordering = ['created_at', '-created_at', 'start_date', '-start_date',
                            'budget_total', '-budget_total']
        if ordering in allowed_ordering:
            qs = qs.order_by(ordering)

        serializer = TripListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TripDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TripRetrieveUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(
            Trip.objects.prefetch_related(
                'trip_destinations__destination',
                'interests__interest',
                'preferences'
            ),
            pk=pk
        )

    def get(self, request, pk):
        trip = self.get_object(pk)
        serializer = TripDetailSerializer(trip)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        trip = self.get_object(pk)
        serializer = TripDetailSerializer(trip, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        trip = self.get_object(pk)
        serializer = TripDetailSerializer(trip, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        trip = self.get_object(pk)
        trip.delete()
        return Response({"message": "Trip deleted."}, status=status.HTTP_204_NO_CONTENT)


class TripPublicListView(APIView):
    """
    GET /api/trips/public/  → All public trips (no auth needed)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Trip.objects.filter(is_public=True).prefetch_related(
            'trip_destinations__destination'
        )
        serializer = TripListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TripUpdateStatusView(APIView):
    """
    PATCH /api/trips/{pk}/update_status/
    Body: { "status": "draft|saved|shared|completed" }
    """
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        trip = get_object_or_404(Trip, pk=pk)
        new_status = request.data.get('status')

        valid_statuses = [s[0] for s in TripStatus.choices]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Valid choices: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        trip.status = new_status
        trip.save(update_fields=['status', 'updated_at'])
        return Response({"message": "Status updated.", "status": trip.status}, status=status.HTTP_200_OK)


class TripGenerateItineraryView(APIView):
    """
    POST /api/trips/{pk}/generate_itinerary/
    AI hook — integrate ai_engine service here when ready.
    """
    permission_classes = [AllowAny]

    def post(self, request, pk):
        trip = get_object_or_404(Trip, pk=pk)

        # -----------------------------------------------
        # AI SERVICE HOOK — plug in when ready
        # from ai_engine.services import generate_trip_itinerary
        # trip.itinerary_json = generate_trip_itinerary(trip)
        # trip.status = TripStatus.SAVED
        # trip.save(update_fields=['itinerary_json', 'status', 'updated_at'])
        # -----------------------------------------------

        return Response(
            {
                "message": "AI engine not integrated yet. Hook is ready.",
                "trip_id": str(trip.id),
            },
            status=status.HTTP_200_OK
        )


# =========================
# TRIP DESTINATIONS
# =========================

class TripDestinationListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        destinations = trip.trip_destinations.select_related('destination').all()
        serializer = TripDestinationSerializer(destinations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)

        if trip.trip_destinations.count() >= trip.max_destinations:
            return Response(
                {"error": f"Maximum {trip.max_destinations} destinations allowed for this trip."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TripDestinationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(trip=trip)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TripDestinationRetrieveUpdateDestroyView(APIView):
    """
    GET    /api/trips/{trip_pk}/destinations/{pk}/
    PUT    /api/trips/{trip_pk}/destinations/{pk}/
    PATCH  /api/trips/{trip_pk}/destinations/{pk}/
    DELETE /api/trips/{trip_pk}/destinations/{pk}/
    """
    permission_classes = [AllowAny]

    def get_object(self, trip_pk, pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        return get_object_or_404(TripDestination, pk=pk, trip=trip)

    def get(self, request, trip_pk, pk):
        destination = self.get_object(trip_pk, pk)
        serializer = TripDestinationSerializer(destination)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, trip_pk, pk):
        destination = self.get_object(trip_pk, pk)
        serializer = TripDestinationSerializer(destination, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, trip_pk, pk):
        destination = self.get_object(trip_pk, pk)
        serializer = TripDestinationSerializer(destination, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, trip_pk, pk):
        destination = self.get_object(trip_pk, pk)
        destination.delete()
        return Response({"message": "Destination removed."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# TRIP INTERESTS
# =========================

class TripInterestListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        interests = trip.interests.select_related('interest').all()
        serializer = TripInterestSerializer(interests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)

        serializer = TripInterestSerializer(data=request.data)
        if serializer.is_valid():
            interest_id = serializer.validated_data['interest'].id
            if trip.interests.filter(interest_id=interest_id).exists():
                return Response(
                    {"error": "This interest is already added to the trip."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(trip=trip)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TripInterestRetrieveUpdateDestroyView(APIView):
    """
    GET    /api/trips/{trip_pk}/interests/{pk}/
    PUT    /api/trips/{trip_pk}/interests/{pk}/
    PATCH  /api/trips/{trip_pk}/interests/{pk}/
    DELETE /api/trips/{trip_pk}/interests/{pk}/
    """
    permission_classes = [AllowAny]

    def get_object(self, trip_pk, pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        return get_object_or_404(TripInterest, pk=pk, trip=trip)

    def get(self, request, trip_pk, pk):
        trip_interest = self.get_object(trip_pk, pk)
        serializer = TripInterestSerializer(trip_interest)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, trip_pk, pk):
        trip_interest = self.get_object(trip_pk, pk)
        serializer = TripInterestSerializer(trip_interest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, trip_pk, pk):
        trip_interest = self.get_object(trip_pk, pk)
        serializer = TripInterestSerializer(trip_interest, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, trip_pk, pk):
        trip_interest = self.get_object(trip_pk, pk)
        trip_interest.delete()
        return Response({"message": "Interest removed."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# TRIP PREFERENCES
# (OneToOne with Trip — sirf ek object per trip)
# =========================

class TripPreferencesView(APIView):
    """
    GET    /api/trips/{trip_pk}/preferences/   → Get preferences (auto-create empty if missing)
    POST   /api/trips/{trip_pk}/preferences/   → Create preferences (error if already exists)
    PUT    /api/trips/{trip_pk}/preferences/   → Full update
    PATCH  /api/trips/{trip_pk}/preferences/   → Partial update
    DELETE /api/trips/{trip_pk}/preferences/   → Delete preferences
    """
    permission_classes = [AllowAny]

    def get(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        preferences, _ = TripPreferences.objects.get_or_create(trip=trip)
        serializer = TripPreferencesSerializer(preferences)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)

        if hasattr(trip, 'preferences'):
            return Response(
                {"error": "Preferences already exist for this trip. Use PATCH/PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TripPreferencesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(trip=trip)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        preferences = get_object_or_404(TripPreferences, trip=trip)
        serializer = TripPreferencesSerializer(preferences, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        preferences = get_object_or_404(TripPreferences, trip=trip)
        serializer = TripPreferencesSerializer(preferences, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        preferences = get_object_or_404(TripPreferences, trip=trip)
        preferences.delete()
        return Response({"message": "Preferences deleted."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# SHARED TRIPS
# =========================

class SharedTripListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        shared_trips = SharedTrip.objects.select_related(
            'trip', 'who_created'
        ).prefetch_related('shared_with_users__user')
        serializer = SharedTripSerializer(shared_trips, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateSharedTripSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trip = get_object_or_404(Trip, id=serializer.validated_data['trip_id'])
        expires_at = serializer.validated_data.get('expires_at')
        shared_with = serializer.validated_data.get('shared_with')

        if hasattr(trip, 'shared_link'):
            return Response(
                {
                    "error": "Trip is already shared.",
                    "shared_trip_id": str(trip.shared_link.id)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        shared_trip = SharedTrip.objects.create(
            trip=trip,
            who_created=request.user if request.user.is_authenticated else None,
            share_token=secrets.token_urlsafe(32),
            expires_at=expires_at
        )

        # Add user if provided
        if shared_with:
            user = get_object_or_404(User, id=shared_with)
            SharedTripUser.objects.create(
                shared_trip=shared_trip,
                user=user
            )

        trip.status = TripStatus.SHARED
        trip.is_public = True
        trip.save(update_fields=['status', 'is_public', 'updated_at'])

        out = SharedTripSerializer(shared_trip, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class SharedTripRetrieveUpdateDestroyView(APIView):
    """
    GET    /api/shared-trips/{pk}/
    PATCH  /api/shared-trips/{pk}/  → Update expiry, add/remove user
    DELETE /api/shared-trips/{pk}/  → Revoke share link
    """
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(
            SharedTrip.objects.select_related('trip', 'who_created')
            .prefetch_related('shared_with_users__user'),
            pk=pk
        )

    def get(self, request, pk):
        shared_trip = self.get_object(pk)
        serializer = SharedTripSerializer(shared_trip, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        shared_trip = self.get_object(pk)

        # Validate
        update_serializer = UpdateSharedTripSerializer(data=request.data, partial=True)
        update_serializer.is_valid(raise_exception=True)

        # Update expires_at
        expires_at = update_serializer.validated_data.get('expires_at')
        if expires_at is not None:
            shared_trip.expires_at = expires_at
            shared_trip.save(update_fields=['expires_at'])

        # Add user
        add_user = update_serializer.validated_data.get('add_user')
        if add_user:
            user = get_object_or_404(User, id=add_user)
            _, created = SharedTripUser.objects.get_or_create(
                shared_trip=shared_trip,
                user=user
            )
            if created:
                return Response({
                    "message": f"User {user.email} added successfully.",
                    "user_id": user.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": f"User {user.email} already has access to this trip."
                }, status=status.HTTP_400_BAD_REQUEST)

        # Remove user
        remove_user = update_serializer.validated_data.get('remove_user')
        if remove_user:
            user = get_object_or_404(User, id=remove_user)
            deleted_count, _ = SharedTripUser.objects.filter(
                shared_trip=shared_trip,
                user=user
            ).delete()

            if deleted_count > 0:
                return Response({
                    "message": f"User {user.email} removed successfully.",
                    "user_id": user.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": f"User {user.email} doesn't have access to this trip."
                }, status=status.HTTP_400_BAD_REQUEST)

        # If only expiry was updated
        return Response({"message": "Expiry date updated successfully."}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        shared_trip = self.get_object(pk)
        trip = shared_trip.trip

        SharedTripUser.objects.filter(shared_trip=shared_trip).delete()
        shared_trip.delete()

        if trip.status == TripStatus.SHARED:
            trip.status = TripStatus.SAVED
            trip.is_public = False
            trip.save(update_fields=['status', 'is_public', 'updated_at'])

        return Response({"message": "Share link revoked."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# SHARED TRIP BY TOKEN (Public Access)
# =========================
class SharedTripByTokenView(APIView):
    """
    GET /api/shared-trips/token/{token}/
    """
    permission_classes = [AllowAny]

    def get(self, request, token):
        shared_trip = get_object_or_404(
            SharedTrip.objects.select_related('trip', 'who_created')
            .prefetch_related('shared_with_users__user'),
            share_token=token
        )

        if shared_trip.expires_at and shared_trip.expires_at < timezone.now():
            return Response(
                {"error": "This share link has expired."},
                status=status.HTTP_410_GONE
            )

        serializer = SharedTripSerializer(shared_trip, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# =========================
# SHARED TRIP USERS - SIMPLE
# =========================

class SharedTripUserListCreateView(APIView):
    """
    GET  /api/shared-trips/{shared_trip_pk}/users/
    POST /api/shared-trips/{shared_trip_pk}/users/
    """
    permission_classes = [AllowAny]

    def get(self, request, shared_trip_pk):
        shared_trip = get_object_or_404(SharedTrip, pk=shared_trip_pk)
        users = shared_trip.shared_with_users.select_related('user').all()

        # Simple flat structure
        data = []
        for su in users:
            data.append({
                "user_id": su.user.id,
                "email": su.user.email,
                "username": su.user.username,
                "shared_at": su.shared_at
            })
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, shared_trip_pk):
        shared_trip = get_object_or_404(SharedTrip, pk=shared_trip_pk)
        serializer = AddSharedTripUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['shared_with']
        user = get_object_or_404(User, id=user_id)

        _, created = SharedTripUser.objects.get_or_create(
            shared_trip=shared_trip, user=user
        )

        if not created:
            return Response(
                {"error": f"User {user.email} already has access to this trip."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": f"Trip shared with {user.email}.",
            "user_id": user.id,
            "user_email": user.email
        }, status=status.HTTP_201_CREATED)


class SharedTripUserDestroyView(APIView):
    """
    DELETE /api/shared-trips/{shared_trip_pk}/users/{user_pk}/
    """
    permission_classes = [AllowAny]

    def delete(self, request, shared_trip_pk, user_pk):
        shared_trip = get_object_or_404(SharedTrip, pk=shared_trip_pk)
        user = get_object_or_404(User, id=user_pk)

        deleted_count, _ = SharedTripUser.objects.filter(
            shared_trip=shared_trip,
            user_id=user_pk
        ).delete()

        if deleted_count == 0:
            return Response(
                {"error": f"User {user.email} doesn't have access to this trip."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": f"User {user.email} removed from shared trip."
        }, status=status.HTTP_204_NO_CONTENT)


# ==============================================================
# USER TRIP VIEWS
# ==============================================================
class UserTripListCreateView(APIView):
    """
    GET  -> Logged-in user ki sari trip mappings list karo
    POST -> Naya user-trip mapping create karo (user automatically request se aayega)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Normal user ko sirf apni trips dikhengi, superuser/staff ko sab
        if request.user.is_staff or request.user.is_superuser:
            user_trips = UserTrip.objects.all()
        else:
            user_trips = UserTrip.objects.filter(user=request.user)

        serializer = UserTripSerializer(user_trips, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = UserTripSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
            except IntegrityError:
                return Response(
                    {"detail": "Is trip ka mapping pehle se maujood hai."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTripDetailView(APIView):
    """
    GET    -> Single user-trip mapping dekho
    PUT    -> Mapping update karo (mostly status: pending/done)
    PACTH  -> Mapping update karo (mostly status: pending/done)
    DELETE -> Mapping delete karo
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        obj = get_object_or_404(UserTrip, pk=pk)
        # Normal user sirf apna object access kar sake
        if not (request.user.is_staff or request.user.is_superuser) and obj.user != request.user:
            return None
        return obj

    def get(self, request, pk, *args, **kwargs):
        user_trip = self.get_object(request, pk)
        if user_trip is None:
            return Response(
                {"detail": "Ye record aapka nahi hai."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = UserTripSerializer(user_trip)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        user_trip = self.get_object(request, pk)
        if user_trip is None:
            return Response(
                {"detail": "Ye record aapka nahi hai."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = UserTripSerializer(
            user_trip, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        user_trip = self.get_object(request, pk)
        if user_trip is None:
            return Response(
                {"detail": "Ye record aapka nahi hai."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = UserTripSerializer(
            user_trip, 
            data=request.data, 
            partial=True,  # ✅ This allows partial updates
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, *args, **kwargs):
        user_trip = self.get_object(request, pk)
        if user_trip is None:
            return Response(
                {"detail": "Ye record aapka nahi hai."},
                status=status.HTTP_403_FORBIDDEN
            )
        user_trip.delete()
        return Response(
            {"detail": "User-Trip mapping delete ho gayi."},
            status=status.HTTP_204_NO_CONTENT
        )


# ==============================================================
# REVIEW VIEWS
# ==============================================================
class ReviewListCreateView(APIView):
    """
    GET  -> Sari reviews list karo (sab dekh sakte hain - public ratings)
    POST -> Nayi review create karo (user automatically request se aayega)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Reviews public hone chahiye taake har trip ke ratings sab dekh sakein
        reviews = Review.objects.all()

        # Optional: ?trip=<uuid> query param se filter bhi ho sake
        trip_id = request.query_params.get('trip')
        if trip_id:
            reviews = reviews.filter(trip__id=trip_id)

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
            except IntegrityError:
                return Response(
                    {"detail": "Aap is trip ko pehle hi review kar chuke hain."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    """
    GET    -> Single review dekho
    PUT    -> Sirf apni review update kar sako
    DELETE -> Sirf apni review delete kar sako
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Review, pk=pk)

    def get(self, request, pk, *args, **kwargs):
        review = self.get_object(pk)
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        review = self.get_object(pk)

        # Sirf owner (ya staff/superuser) update kar sake
        if review.user != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "Aap sirf apni review update kar sakte hain."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReviewSerializer(
            review, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk, *args, **kwargs):
        review = self.get_object(pk)

        # Sirf owner (ya staff/superuser) update kar sake
        if review.user != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "Aap sirf apni review update kar sakte hain."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReviewSerializer(
            review, 
            data=request.data, 
            partial=True,  # Allows partial updates
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, pk, *args, **kwargs):
        review = self.get_object(pk)

        # Sirf owner (ya staff/superuser) delete kar sake
        if review.user != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "Aap sirf apni review delete kar sakte hain."},
                status=status.HTTP_403_FORBIDDEN
            )

        review.delete()
        return Response(
            {"detail": "Review Is successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )