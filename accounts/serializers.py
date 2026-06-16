from rest_framework import serializers
from .models import CustomUser, Interest, UserPreferences, UserVehicle, Notification, SocialAccount

# ==========================================

# USER PROFILE SERIALIZER

# ==========================================

class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser

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

        read_only_fields = ['id', 'is_verified']


# ==========================================

# SIGNUP SERIALIZER

# ==========================================

class SignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=6)

    confirm_password = serializers.CharField(write_only=True, min_length=6)

    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser

        fields = [
            'username',
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name'
        ]

    def validate(self, attrs):

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):

        # Remove confirm_password before creating user
        validated_data.pop('confirm_password')

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        return user
    
# ==========================================
# INTEREST SERIALIZER
# ==========================================
class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']
        
        
# ==========================================
# USER PREFERENCES SERIALIZER
# ==========================================
class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = [
            'id',
            'user',
            'travel_interests',
            'preferred_transport_modes',
            'preferred_seat_class',
            'food_preferences',
            'travel_style',
            'default_group_size',
            'max_budget_per_trip',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']     
        
        
# ==========================================
# USER PROFILE SERIALIZER — sab kuch ek jagah
# ==========================================
class UserProfileSerializer(serializers.ModelSerializer):

    # Nested preferences — user ki preferences bhi saath aayengi
    preferences = UserPreferencesSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar_file',
            'home_city',
            'language',
            'is_verified',
            'preferences',
        ]
        read_only_fields = ['id', 'is_verified']

    # Update method — PUT aur PATCH dono ke liye zaroori
    def update(self, instance, validated_data):

        # Har field ko update karo — agar nahi bheja toh purani value rakho
        instance.username    = validated_data.get('username',    instance.username)
        instance.email       = validated_data.get('email',       instance.email)
        instance.first_name  = validated_data.get('first_name',  instance.first_name)
        instance.last_name   = validated_data.get('last_name',   instance.last_name)
        instance.avatar_file = validated_data.get('avatar_file', instance.avatar_file)
        instance.home_city   = validated_data.get('home_city',   instance.home_city)
        instance.language    = validated_data.get('language',    instance.language)

        # DB mein save karo
        instance.save()

        return instance
    

# ==========================================
# NOTIFICATION SERIALIZER
# ==========================================
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'type',
            'title',
            'body',
            'read_at',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']