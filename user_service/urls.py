from django.urls import path
from .views import CreateProfileView
from .views import LoginView, LogoutView

urlpatterns = [
    path('create-profile/', CreateProfileView.as_view(), name='create-profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]