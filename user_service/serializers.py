from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
        }

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'is_tutor']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        user, created = User.objects.get_or_create(
            username=user_data['email'], 
            defaults={
                'email': user_data['email'], 
                'password': user_data['password'],
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', '')
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
        else:
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()

        profile, created = Profile.objects.get_or_create(user=user)
        profile.is_tutor = validated_data.get('is_tutor', profile.is_tutor)
        profile.save()

        return profile

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        attrs['user'] = user
        return attrs