from rest_framework import serializers
from .models import *
from user_service.models import User
from user_service.serializers import ProfileSerializer

class SubjectSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(source='user.profile', read_only=True)  

    class Meta:
        model = Subject
        fields = '__all__'

class LessonParticipantSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(source='user.profile', read_only=True)  

    class Meta:
        model = LessonParticipant
        fields = ['profile', 'status', 'updated_at', 'rating']

class LessonSerializer(serializers.ModelSerializer):
    tutor = ProfileSerializer(source='tutor.profile', read_only=True)  
    subject = SubjectSerializer(read_only=True)
    participants = LessonParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'

    def create(self, validated_data):
        participants_data = self.context['request'].data.get('participants', [])
        lesson = Lesson.objects.create(**validated_data)

        for user_id in participants_data:
            LessonParticipant.objects.create(
                user_id=user_id,
                lesson=lesson,
                status=LessonParticipant.Status.AWAITING_CONFIRMATION
            )

        return lesson

    def update(self, instance, validated_data):
        participants_data = self.context['request'].data.get('participants', [])

        instance = super().update(instance, validated_data)

        existing_participants = {p.user_id: p for p in instance.participants.all()}

        new_participants = set(participants_data)
        for user_id in new_participants:
            if user_id not in existing_participants:
                LessonParticipant.objects.create(
                    user_id=user_id,
                    lesson=instance,
                    status=LessonParticipant.Status.AWAITING_CONFIRMATION
                )

        for user_id in existing_participants:
            if user_id not in new_participants:
                existing_participants[user_id].delete()

        return instance
    
class SubjectLessonCountSerializer(serializers.Serializer):
    subject = serializers.CharField(source='subject__title')
    colorId = serializers.CharField(source='subject__colorId')
    lesson_count = serializers.IntegerField()