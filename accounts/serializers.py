from rest_framework import serializers
from django.utils import timezone
from .models import CustomUser, Interest, UserPreferences, UserVehicle, Notification, SocialAccount


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar_file', 'home_city', 'language', 'is_verified'
        ]
        read_only_fields = ['id', 'is_verified']


class SignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password',
            'confirm_password', 'first_name', 'last_name'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserPreferencesSerializer(serializers.ModelSerializer):

    # ✅ CHECK ADDED: selected_interests field (Interest model se link, multi-select)
    selected_interests = serializers.PrimaryKeyRelatedField(
        queryset=Interest.objects.all(),
        many=True
    )

    class Meta:
        model = UserPreferences
        fields = [
            'id', 'user', 'travel_interests', 'preferred_transport_modes',
            'preferred_seat_class', 'food_preferences', 'travel_style',
            'default_group_size', 'max_budget_per_trip',
            'selected_interests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    # ✅ CHECK ADDED: max 6, min 1 interests select hone chahiye
    def validate_selected_interests(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                "Kam az kam 1 interest select karna zaroori hai."
            )
        if len(value) > 6:
            raise serializers.ValidationError(
                "Aap zyada se zyada 6 interests select kar sakte hain."
            )
        return value


class UserProfileSerializer(serializers.ModelSerializer):

    preferences = UserPreferencesSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar_file', 'home_city', 'language', 'is_verified', 'preferences',
        ]
        read_only_fields = ['id', 'is_verified']

    def update(self, instance, validated_data):
        instance.username    = validated_data.get('username',    instance.username)
        instance.email       = validated_data.get('email',       instance.email)
        instance.first_name  = validated_data.get('first_name',  instance.first_name)
        instance.last_name   = validated_data.get('last_name',   instance.last_name)
        instance.avatar_file = validated_data.get('avatar_file', instance.avatar_file)
        instance.home_city   = validated_data.get('home_city',   instance.home_city)
        instance.language    = validated_data.get('language',    instance.language)
        instance.save()
        return instance


# ✅ CHECK ADDED: token_expires_at future mein hona chahiye
class SocialAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialAccount
        fields = [
            'id', 'user', 'provider', 'provider_user_id',
            'access_token', 'refresh_token', 'token_expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_token_expires_at(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Token expiry purana nahi ho sakta. Future ka date/time dalein."
            )
        return value


# ✅ CHECK ADDED: read_at future mein nahi ho sakta
class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'type', 'title',
            'body', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_read_at(self, value):
        if value and value > timezone.now():
            raise serializers.ValidationError(
                "Read time future mein nahi ho sakta."
            )
        return value