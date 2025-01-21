from django.urls import path
from . import views

urlpatterns = [
    path('topup/', views.top_up, name='topup'),
    path('withdraw/', views.withdraw, name='withdraw'),
    # path('transfer/', views.transfer, name='transfer'),
    path('balance/', views.get_user_balance, name='get_user_balance'),
    path('monthly-income/', views.get_income, name='get_transfer_income_for_current_month'),
]
