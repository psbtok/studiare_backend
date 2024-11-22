from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from .models import Lesson
from .serializers import LessonSerializer

class LessonPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100    

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LessonPagination  
    filter_backends = [filters.OrderingFilter] 
    ordering_fields = ['date_start', 'date_end']
    ordering = ['-date_start']

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(tutor=user)

    def perform_update_start(self, serializer):
        serializer.save()
