from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate
from rest_framework.parsers import MultiPartParser, FormParser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
        }

class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutor
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    tutor = TutorSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['user', 'is_tutor', 'tutor', 'profile_picture']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        user, created = User.objects.get_or_create(
            username=user_data['email'], 
            defaults={
                'email': user_data['email'], 
                'password': user_data['password'],
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()

        profile, created = Profile.objects.get_or_create(user=user)        
        
        profile.save()
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            if 'password' in user_data and user_data['password']:
                user.set_password(user_data['password'])
            user.save()

        instance.is_tutor = validated_data.get('is_tutor', instance.is_tutor)
        if instance.is_tutor and not instance.tutor:
            tutor = Tutor.objects.create()
            instance.tutor = tutor

        if 'profile_picture' in validated_data and validated_data['profile_picture'] is not None:
            instance.profile_picture = validated_data['profile_picture']

        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        attrs['user'] = user
        return attrs
    
