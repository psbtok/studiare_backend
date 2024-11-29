from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import Lesson
from .serializers import LessonSerializer
from django.shortcuts import get_object_or_404
from user_service.models import User
from django.utils.timezone import make_aware
from datetime import datetime

class LessonPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class LessonFilter(django_filters.FilterSet):
    date_start_from = django_filters.DateTimeFilter(
        field_name='date_start', 
        lookup_expr='gte', 
        label='Start from date'
    )

    class Meta:
        model = Lesson
        fields = ['tutor', 'date_start_from', 'date_end', 'subject', 'isConfirmed']

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LessonPagination  
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = LessonFilter
    ordering_fields = ['date_start', 'date_end']
    ordering = ['-date_start']

    def perform_create(self, serializer):
        user = self.request.user
        student_id = self.request.data.get('student')
        student = get_object_or_404(User, pk=student_id)
        serializer.save(tutor=user, student=student)
