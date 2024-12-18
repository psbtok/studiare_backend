from django.urls import path
from .views import CreateProfileView
from .views import *

urlpatterns = [
    path('profile/create/', CreateProfileView.as_view(), name='create-profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/edit/', EditProfileView.as_view(), name='edit-profile'),
    path('profile/get/', GetProfileByIdView.as_view(), name='get-profile'),
    path('users/by-full-name/', GetUsersByFullNameView.as_view(), name='get-users-by-full-name'),
]