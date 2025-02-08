from rest_framework import serializers
from .models import Lesson, Subject
from user_service.serializers import ProfileSerializer

class SubjectSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(source='user.profile', read_only=True)  

    class Meta:
        model = Subject
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    student = ProfileSerializer(source='student.profile', read_only=True)  
    tutor = ProfileSerializer(source='tutor.profile', read_only=True)  
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'