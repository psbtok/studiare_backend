from rest_framework import serializers
from .models import Lesson
from user_service.serializers import UserSerializer

class LessonSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)  

    class Meta:
        model = Lesson
        fields = '__all__'
