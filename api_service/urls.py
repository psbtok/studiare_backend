from django.urls import path
from .views import CreateProfileView

urlpatterns = [
    path('create-profile/', CreateProfileView.as_view(), name='create-profile'),
]