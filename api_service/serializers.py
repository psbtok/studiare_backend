from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data) 
        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'is_tutor']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        user, created = User.objects.get_or_create(
            username=user_data['username'], 
            defaults={'email': user_data['email'], 'password': user_data['password']}
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
        
        profile, created = Profile.objects.get_or_create(user=user)

        profile.is_tutor = validated_data.get('is_tutor', profile.is_tutor)
        profile.save()

        return profile
