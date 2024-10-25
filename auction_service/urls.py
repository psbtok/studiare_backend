from django.urls import path
from .views import LotCreateView, BidCreateView, LotListView, LotDetailView

urlpatterns = [
    path('lots/', LotListView.as_view(), name='get-lots'),
    path('lots/<int:pk>/', LotDetailView.as_view(), name='get-lot'),
    path('lots/create/', LotCreateView.as_view(), name='create-lot'),
    path('bids/create/', BidCreateView.as_view(), name='create-bid'),
]