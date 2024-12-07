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
from django.db.models import Q

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
        """
        Фильтрует список уроков, если передан userId.
        Уроки, в которых текущий пользователь является студентом или преподавателем, будут возвращены.
        """
        user = self.request.user
        user_id = self.request.query_params.get('userId')  # Получаем userId из параметров запроса
        
        # Если userId присутствует в запросе, фильтруем по этому пользователю
        if user_id:
            return Lesson.objects.filter(
                Q(tutor_id=user_id) | Q(student_id=user_id)
            )
        
        # Если userId не передан, возвращаем все уроки, связанные с текущим авторизованным пользователем
        return Lesson.objects.filter(
            Q(tutor=user) | Q(student=user)
        )

    def perform_create(self, serializer):
        user = self.request.user
        student_id = self.request.data.get('student')
        student = get_object_or_404(User, pk=student_id)
        serializer.save(tutor=user, student=student)