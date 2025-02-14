from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'subjects', SubjectViewSet, basename='subject')

urlpatterns = [
    path('', include(router.urls)),
    path('lesson-counts/', SubjectLessonCountView.as_view(), name='lesson-counts'),
]
