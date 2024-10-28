from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .models import Lot
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache

class LotCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LotCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BidCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        lot_id = request.data.get('lot')  
        amount = request.data.get('amount')

        try:
            lot = Lot.objects.get(pk=lot_id)
        except Lot.DoesNotExist:
            return Response({"detail": "Lot not found."}, status=status.HTTP_404_NOT_FOUND)

        highest_bid = lot.bids.order_by('-amount').first()

        if highest_bid and float(amount) <= float(highest_bid.amount):
            return Response({"detail": "Your bid must be higher than the current highest bid."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BidSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(bidder=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LotListView(generics.ListAPIView):
    queryset = Lot.objects.all()
    serializer_class = LotListSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        total_count = cache.get('total_lots_count')

        if total_count is None:
            total_count = Lot.objects.count()
            cache.set('total_lots_count', total_count, timeout=60*5) 

        response = super().list(request, *args, **kwargs)

        return Response(response.data)

class LotDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            lot = Lot.objects.get(pk=pk)
        except Lot.DoesNotExist:
            return Response({"detail": "Lot not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LotDetailSerializer(lot)
        return Response(serializer.data, status=status.HTTP_200_OK)
