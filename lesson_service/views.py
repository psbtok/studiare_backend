from rest_framework import viewsets, permissions, filters  
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import Lesson, Subject, LessonParticipant
from .serializers import LessonSerializer, SubjectSerializer
from django.shortcuts import get_object_or_404
from user_service.models import User
from django.db.models import Q
from payment_service.services import PaymentService  
from django.core.exceptions import ValidationError  
from django.utils import timezone
from datetime import timedelta

class SubjectFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    colorId = django_filters.NumberFilter(field_name='colorId')

    class Meta:
        model = Subject
        fields = ['title', 'colorId']

class SubjectPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SubjectPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SubjectFilter
    ordering_fields = ['title', 'colorId', 'id']  
    ordering = ['-id']

    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LessonPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class LessonFilter(django_filters.FilterSet):
    date_end_from = django_filters.DateTimeFilter(
        field_name='date_end', 
        lookup_expr='gte', 
        label='Start from date'
    )
    date_end_to = django_filters.DateTimeFilter(
        field_name='date_end', 
        lookup_expr='lt', 
        label='End at date'
    )

    class Meta:
        model = Lesson
        fields = ['tutor', 'date_end_from', 'date_end_to', 'date_end', 'subject']

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LessonPagination  
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = LessonFilter
    ordering_fields = ['date_start', 'date_end']
    ordering = ['-date_start']

    def get_queryset(self):
        user = self.request.user
        user_id = self.request.query_params.get('userId') 
        
        if user_id:
            return Lesson.objects.filter(
                Q(tutor_id=user_id) | Q(participants__user_id=user_id)
            ).distinct()
        
        return Lesson.objects.filter(
            Q(tutor=user) | Q(participants__user=user)
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        participant_ids = self.request.data.get('participants', [])
        subject_id = self.request.data.get('subject')
        subject = get_object_or_404(Subject, pk=subject_id)
        participants = []
        for participant_id in participant_ids:
            participant_user = get_object_or_404(User, pk=participant_id)  
            participants.append(participant_user)

        serializer.save(tutor=user, subject=subject)

    def perform_update(self, serializer):
        instance = self.get_object()
        action = self.request.data.get('action')  # Get the action from the request

        if action not in ['cancel', 'confirm', 'conduct']:
            serializer.save()
            return

        user = self.request.user  # Current user making the request
        current_participant = instance.participants.filter(user=user).first()

        if not current_participant and instance.tutor != user:
            raise ValidationError("You are not a participant or tutor of this lesson.")

        if action == 'confirm' and current_participant:
            # Update the participant's status to 'confirmed'
            current_participant.status = LessonParticipant.Status.CONFIRMED
            current_participant.save()

        elif action == 'conduct':
            # Check if the user is the tutor
            if instance.tutor != user:
                raise ValidationError("Only the tutor can mark the lesson as conducted.")

            # Update the participant's status to 'conducted'
            current_participant.status = LessonParticipant.Status.CONDUCTED
            current_participant.save()

            # Transfer payment from student to tutor
            for participant in instance.participants.filter(status=LessonParticipant.Status.CONFIRMED):
                try:
                    PaymentService.transfer(sender=participant.user, receiver=instance.tutor, amount=instance.price)
                except Exception as e:
                    raise ValidationError(f"Failed to transfer funds: {str(e)}")

        elif action == 'cancel':
            # If the tutor cancels, cancel the lesson for all participants
            if instance.tutor == user:
                print("Tutor is canceling the lesson. Cancelling all participants.")
                for participant in instance.participants.all():
                    print(f"Cancelling participant: {participant.user.id} with current status: {participant.status}")
                    participant.status = LessonParticipant.Status.CANCELLED
                    participant.save()
                print('All participants have been cancelled.')
            else:
                # If a student cancels, handle late cancellation fees
                now = timezone.now()
                time_difference = instance.date_start - now

                if time_difference < timedelta(hours=3):
                    # Apply a 30% cancellation fee
                    compensation = int(instance.price * 0.3)
                    try:
                        PaymentService.transfer(sender=user, receiver=instance.tutor, amount=compensation)
                    except Exception as e:
                        raise ValidationError(f"Failed to transfer cancellation fee: {str(e)}")

                # Update the participant's status to 'cancelled'
                current_participant.status = LessonParticipant.Status.CANCELLED
                current_participant.save()