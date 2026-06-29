from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'profile_picture', 'date_of_birth', 'is_active', 'is_staff', 'date_joined', 'groups', 'channels')
        read_only_fields = ('id', 'date_joined')

    def get_groups(self, obj):
        return ', '.join([group.name for group in obj.groups.all()]) if obj.groups.exists() else 'No Group'


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm Password')

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'date_of_birth')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
