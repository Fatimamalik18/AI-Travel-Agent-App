from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.parsers import MultiPartParser, FormParser

from .models import CustomUser, Interest, UserPreferences, Notification
from .serializers import UserPreferenceInterestSerializer, CustomUserSerializer, SignupSerializer, InterestSerializer, UserPreferencesSerializer, UserProfileSerializer, NotificationSerializer


# =========================
# USERS LIST + CREATE
# =========================
class UserListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# USER DETAIL
# =========================
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        if str(request.user.id) != str(pk):
            return Response(
                {"detail": "You do not have permission to update another user's account."},
                status=status.HTTP_403_FORBIDDEN
            )

        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if str(request.user.id) != str(pk):
            return Response(
                {"detail": "You do not have permission to delete another user's account."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        user.delete()
        return Response({"detail": "User deleted successfully."}, status=status.HTTP_200_OK)


# =========================
# LOGIN
# =========================
class LoginView(APIView):

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response({"message": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)

        # ✅ NEW: role ka naam JWT token ke andar bhi daal diya
        refresh["role"] = user.role.name if user.role else None

        return Response({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.name if user.role else None,   # ✅ NEW
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        })


# =========================
# SIGNUP
# =========================
class SignupView(APIView):

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "id": str(user.id),
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# INTEREST LIST + CREATE
# =========================
class InterestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        interests = Interest.objects.all()
        serializer = InterestSerializer(interests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserPreferenceInterestSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            preferences = serializer.save()

            return Response(
                {
                    "message": "Interests saved successfully",
                    "selected_interests": list(
                        preferences.selected_interests.values_list(
                            "name", flat=True
                        )
                    )
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================
# INTEREST DETAIL
# =========================
class InterestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        interest = get_object_or_404(Interest, pk=pk)
        serializer = InterestSerializer(interest)
        return Response(serializer.data)

    def delete(self, request, pk):
        interest = get_object_or_404(Interest, pk=pk)
        interest.delete()
        return Response({"detail": "Interest deleted successfully."}, status=status.HTTP_200_OK)


# ==========================================
# USER INTERESTS — SELECT/SAVE (max 6, min 1)
# ==========================================
class UserInterestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(
            {"interests": serializer.data.get("interests", [])},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = CustomUserSerializer(
            request.user,
            data={"interests": request.data.get("interests", [])},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# USER PREFERENCES CRUD API
# ==========================================
class UserPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            preferences = UserPreferences.objects.get(user=request.user)
            serializer = UserPreferencesSerializer(preferences)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserPreferences.DoesNotExist:
            return Response(
                {"detail": "Preferences not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        if UserPreferences.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Preferences already exist. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserPreferencesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            preferences = UserPreferences.objects.get(user=request.user)
        except UserPreferences.DoesNotExist:
            return Response(
                {"detail": "Preferences not found. Use POST to create first."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserPreferencesSerializer(preferences, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            preferences = UserPreferences.objects.get(user=request.user)
        except UserPreferences.DoesNotExist:
            return Response(
                {"detail": "Preferences not found. Use POST to create first."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserPreferencesSerializer(
            preferences,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            preferences = UserPreferences.objects.get(user=request.user)
            preferences.delete()
            return Response(
                {"detail": "Preferences deleted successfully."},
                status=status.HTTP_200_OK
            )
        except UserPreferences.DoesNotExist:
            return Response(
                {"detail": "Preferences not found."},
                status=status.HTTP_404_NOT_FOUND
            )


# ==========================================
# USER PROFILE API
# ==========================================
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# NOTIFICATION LIST + CREATE API
# ==========================================
class NotificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# NOTIFICATION DETAIL API
# ==========================================
class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        serializer = NotificationSerializer(
            notification,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.delete()
        return Response(
            {"detail": "Notification deleted successfully."},
            status=status.HTTP_200_OK
        )


# ==========================================
# UPDATE NOTIFICATION — SEEN CHECK
# ==========================================
class UpdateNotification(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            notification = get_object_or_404(Notification, pk=pk, user=request.user)

            if notification.read_at is not None:
                return Response(
                    {"detail": "seen"},
                    status=status.HTTP_200_OK
                )

            return Response({"detail": "New Notification"}, status=status.HTTP_200_OK)

        except Notification.DoesNotExist:
            return Response(
                {"detail": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND
            )