from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # Specifying fields you want to expose via the API
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'avatar_file', 
            'home_city', 
            'language', 
            'is_verified'
        ]
        # ID and verification status shouldn't be directly editable by regular users
        read_only_fields = ['id', 'is_verified']