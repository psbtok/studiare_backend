from rest_framework import serializers
from .models import Lesson
from user_service.serializers import ProfileSerializer

class LessonSerializer(serializers.ModelSerializer):
    student = ProfileSerializer(source='student.profile', read_only=True)  
    tutor = ProfileSerializer(source='tutor.profile', read_only=True)  

    class Meta:
        model = Lesson
        fields = '__all__'
