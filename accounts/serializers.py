from rest_framework import serializers
from django.utils import timezone
from .models import CustomUser, Interest, UserPreferences, UserVehicle, Notification, SocialAccount, Role


class CustomUserSerializer(serializers.ModelSerializer):

    # ✅ CHECK ADDED: ab UUID ki jagah "name" se interest select hoga
    interests = serializers.SlugRelatedField(
        queryset=Interest.objects.all(),
        slug_field='name',
        many=True,
        required=False
    )

    # ✅ NEW: role ka naam (read-only)
    role = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar_file', 'home_city', 'language', 'is_verified',
            'interests', 'role'
        ]
        read_only_fields = ['id', 'is_verified']

    def validate_interests(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                "Kam az kam 1 interest select karna zaroori hai."
            )
        if len(value) > 6:
            raise serializers.ValidationError(
                "Aap zyada se zyada 6 interests select kar sakte hain."
            )
        return value


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


# ✅ NEW: Role serializer (agar kabhi role list/detail API banani ho)
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name', 'description', 'created_at']
        read_only_fields = ['created_at']


class UserPreferenceInterestSerializer(serializers.Serializer):
    interests = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        max_length=6
    )

    def validate_interests(self, value):
        interests = Interest.objects.filter(name__in=value)

        if interests.count() != len(set(value)):
            found = set(interests.values_list("name", flat=True))
            missing = list(set(value) - found)
            raise serializers.ValidationError(
                f"Invalid interests: {missing}"
            )

        return value

    def save(self, **kwargs):
        user = self.context["request"].user

        preferences, _ = UserPreferences.objects.get_or_create(
            user=user
        )

        interests = Interest.objects.filter(
            name__in=self.validated_data["interests"]
        )

        preferences.selected_interests.set(interests)
        preferences.save()

        return preferences


class UserPreferencesSerializer(serializers.ModelSerializer):


    class Meta:
        model = UserPreferences
        fields = [
            'id',
            'user',
            'preferred_transport_modes',
            'travel_interests',
            'preferred_seat_class',
            'food_preferences',
            'travel_style',
            'default_group_size',
            'max_budget_per_trip',
            'created_at',
            'updated_at'
            
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at'
        ]


class UserProfileSerializer(serializers.ModelSerializer):

    preferences = UserPreferencesSerializer(read_only=True)

    # ✅ CHECK ADDED: yahan bhi name se interests select honge
    interests = serializers.SlugRelatedField(
        queryset=Interest.objects.all(),
        slug_field='name',
        many=True,
        required=False
    )

    # ✅ NEW: role ka naam (read-only)
    role = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar_file', 'home_city', 'language', 'is_verified',
            'interests', 'preferences', 'role'
        ]
        read_only_fields = ['id', 'is_verified']

    def validate_interests(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                "Kam az kam 1 interest select karna zaroori hai."
            )
        if len(value) > 6:
            raise serializers.ValidationError(
                "Aap zyada se zyada 6 interests select kar sakte hain."
            )
        return value

    def update(self, instance, validated_data):
        interests = validated_data.pop('interests', None)

        instance.username    = validated_data.get('username',    instance.username)
        instance.email       = validated_data.get('email',       instance.email)
        instance.first_name  = validated_data.get('first_name',  instance.first_name)
        instance.last_name   = validated_data.get('last_name',   instance.last_name)
        instance.avatar_file = validated_data.get('avatar_file', instance.avatar_file)
        instance.home_city   = validated_data.get('home_city',   instance.home_city)
        instance.language    = validated_data.get('language',    instance.language)
        instance.save()

        if interests is not None:
            instance.interests.set(interests)

        return instance


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