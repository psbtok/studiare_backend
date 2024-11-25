from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
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
        fields = ['user', 'is_tutor', 'tutor']

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

        if profile.is_tutor and not profile.tutor:
            tutor = Tutor.objects.create()
            profile.tutor = tutor

        profile.save()
        return profile
    
    def update(self, instance, validated_data):
        print('update')
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            if 'password' in user_data:
                user.set_password(user_data['password'])
            user.save()

        instance.is_tutor = validated_data.get('is_tutor', instance.is_tutor)

        if instance.is_tutor and not instance.tutor:
            tutor = Tutor.objects.create()
            instance.tutor = tutor

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
    
