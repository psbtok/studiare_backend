from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('user_service.urls')),
    path('api/', include('auction_service.urls')),
]