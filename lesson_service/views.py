from rest_framework import viewsets, permissions, filters  
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

from user_service.serializers import TutorSerializer
from .models import Lesson, Subject, LessonParticipant
from .serializers import *
from django.shortcuts import get_object_or_404
from user_service.models import Profile, Tutor, User
from django.db.models import Q
from payment_service.services import PaymentService  
from django.core.exceptions import ValidationError  
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from rest_framework.views import APIView

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

        subject_id = self.request.data.get('subject')
        try:
            subject = get_object_or_404(Subject, pk=subject_id)
        except:
            if not action:
                raise ValidationError("Subject not found.")

        if action not in ['cancel', 'confirm', 'conduct']:
            serializer.save(subject=subject)
            return

        user = self.request.user  # Current user making the request
        current_participant = instance.participants.filter(user=user).first()

        if not current_participant and instance.tutor != user:
            raise ValidationError("You are not a participant or tutor of this lesson.")

        if action == 'confirm' and current_participant:
            current_participant.status = LessonParticipant.Status.CONFIRMED
            current_participant.save()

        elif action == 'conduct':
            # Check if the user is the tutor
            if instance.tutor != user:
                raise ValidationError("Only the tutor can mark the lesson as conducted.")

            # Transfer payment from student to tutor
            for participant in instance.participants.filter(status=LessonParticipant.Status.CONFIRMED):
                try:
                    PaymentService.transfer(sender=participant.user, receiver=instance.tutor, amount=instance.price)
                    participant.status = LessonParticipant.Status.CONDUCTED
                    participant.save()
                except Exception as e:
                    raise ValidationError(f"Failed to transfer funds: {str(e)}")
                
            # Transfer payment from student to tutor
            for participant in instance.participants.filter(status=LessonParticipant.Status.AWAITING_CONFIRMATION):
                participant.status = LessonParticipant.Status.CANCELLED
                participant.save()


        elif action == 'cancel':
            # If the tutor cancels, cancel the lesson for all participants
            if instance.tutor == user:
                for participant in instance.participants.all():
                    participant.status = LessonParticipant.Status.CANCELLED
                    participant.save()
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
                if not current_participant.status == LessonParticipant.Status.CONDUCTED:
                    current_participant.status = LessonParticipant.Status.CANCELLED
                current_participant.save()

class LessonStatisticsBySubjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')
        chart_type = request.query_params.get('chart_type', 'subject')

        if not date_start or not date_end:
            return Response(
                {"error": "Both date_start and date_end are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if chart_type != 'subject':
            return Response(
                {"error": "Only 'subject' chart_type is supported at the moment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filter lessons within the specified date range
        lessons = Lesson.objects.filter(
            date_start__gte=date_start,
            date_end__lte=date_end,
            tutor=request.user  # Only count lessons for the authenticated user
        )

        # Annotate the count of lessons per subject and include subject__colorId
        subject_lesson_counts = lessons.values('subject__title', 'subject__colorId').annotate(
            lesson_count=Count('id')
        ).filter(lesson_count__gt=0)

        # Serialize the data
        serializer = SubjectLessonCountSerializer(subject_lesson_counts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateRatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        lesson_id = request.data.get('lesson_id')
        rating = request.data.get('rating')

        if lesson_id is None or rating is None:
            return Response({'detail': 'Lesson ID and rating are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if rating > 5 or rating < 1:
            return Response({'detail': 'Rating is supposed to be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        lesson_participant = get_object_or_404(LessonParticipant, lesson_id=lesson_id, user=request.user)
        
        previous_rating = lesson_participant.rating

        lesson_participant.rating = rating
        lesson_participant.save()

        lesson = get_object_or_404(Lesson, id=lesson_id)
        tutor = get_object_or_404(Profile, user=lesson.tutor.id).tutor

        if isinstance(tutor.totalRating, int) and isinstance(tutor.peopleReacted, int):
            tutor.totalRating += (rating - previous_rating)
            tutor.peopleReacted += 1
        else:
            tutor.totalRating = rating
            tutor.peopleReacted = 1
        
        tutor.save()

        tutor_serializer = TutorSerializer(tutor, partial=True)

        return Response({
            'tutor': tutor_serializer.data 
        }, status=status.HTTP_200_OK)