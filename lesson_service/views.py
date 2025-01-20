from rest_framework import viewsets, permissions, filters, serializers  
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import Lesson
from .serializers import LessonSerializer
from django.shortcuts import get_object_or_404
from user_service.models import User
from django.db.models import Q
from payment_service.services import PaymentService  
from django.core.exceptions import ValidationError  
from django.utils import timezone
from datetime import timedelta

class LessonPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class LessonFilter(django_filters.FilterSet):
    date_start_from = django_filters.DateTimeFilter(
        field_name='date_start', 
        lookup_expr='gte', 
        label='Start from date'
    )
    date_start_to = django_filters.DateTimeFilter(
        field_name='date_start', 
        lookup_expr='lt', 
        label='End at date'
    )

    class Meta:
        model = Lesson
        fields = ['tutor', 'date_start_from', 'date_start_to', 'date_end', 'subject', 'isConfirmed']

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
                Q(tutor_id=user_id) | Q(student_id=user_id)
            )
        
        return Lesson.objects.filter(
            Q(tutor=user) | Q(student=user)
        )

    def perform_create(self, serializer):
        user = self.request.user
        student_id = self.request.data.get('student')
        student = get_object_or_404(User, pk=student_id)
        serializer.save(tutor=user, student=student)

    def perform_update(self, serializer):
        instance = self.get_object()
        is_conducted = self.request.data.get('isConducted')
        action = self.request.data.get('action')

        if is_conducted and not instance.isConducted and action=='conduct':
            student = instance.student
            tutor = instance.tutor
            price = instance.price

            try:
                PaymentService.transfer(sender=student, receiver=tutor, amount=price)
            except Exception as e:
                raise ValidationError(f"Failed to transfer funds: {str(e)}")
            
        elif (action == 'cancel' and 
            not instance.isConducted and 
            not instance.isCancelled and
            instance.isConfirmed
        ):
            now = timezone.now()
            time_difference = instance.date_start - now
            student = instance.student
            tutor = instance.tutor
            user = self.request.user
            if time_difference < timedelta(hours=3) and user.id == student.id:
                compensation = int(instance.price * 0.3)
                try:
                    PaymentService.transfer(sender=student, receiver=tutor, amount=compensation)
                except Exception as e:
                    raise ValidationError(f"Failed to transfer funds: {str(e)}")
                
        serializer.save()