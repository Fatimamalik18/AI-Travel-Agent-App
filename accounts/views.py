from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser
from .serializers import CustomUserSerializer

class UserListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # Explicit GET method to list all users
    def get(self, request, *args, **kwargs):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Explicit POST method to create a user
    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2. Handles retrieving, updating, and deleting a single user manually
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # Explicit GET method for a single user
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Explicit PUT method to fully update a user
    def put(self, request, pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user, data=request.data) # Use partial=True if you want PATCH behavior
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Explicit DELETE method to remove a user
    def delete(self, request, pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return Response(
            {"detail": "User deleted successfully."}, 
            status=status.HTTP_204_NO_CONTENT
        )
    

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(
            username=username,
            password=password
        )

        if not user:
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "id": str(user.id),
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        })