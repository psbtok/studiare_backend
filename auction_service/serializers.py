from rest_framework import serializers
from .models import Lot, Bid

class LotCreateSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(read_only=True) 

    class Meta:
        model = Lot
        fields = ['seller', 'title', 'description', 'starting_price', 'is_reserve', 'reserve_price', 'start_datetime', 'end_datetime', 'image']

    def validate(self, data):
        if data['is_reserve'] and data['reserve_price'] <= data['starting_price']:
            raise serializers.ValidationError("Reserve price must be greater than starting price.")
        return data
    
class BidSerializer(serializers.ModelSerializer):
    bidder = serializers.PrimaryKeyRelatedField(read_only=True) 

    class Meta:
        model = Bid
        fields = ['id', 'amount', 'lot', 'bidder']

class LotListSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(read_only=True) 
    last_bid = serializers.SerializerMethodField()

    class Meta:
        model = Lot
        fields = ['id', 'title', 'starting_price', 
                  'is_reserve', 'end_datetime', 
                  'seller', 'last_bid']

    def get_last_bid(self, obj):
        last_bid = obj.bids.order_by('-id').first()
        return BidSerializer(last_bid).data if last_bid else None

class LotDetailSerializer(serializers.ModelSerializer):
    last_bid = serializers.SerializerMethodField()
    bids = serializers.SerializerMethodField()

    class Meta:
        model = Lot
        fields = ['id', 'title', 'description', 'starting_price', 
                  'is_reserve', 'reserve_price', 'start_datetime', 
                  'end_datetime', 'seller', 'last_bid', 'bids']

    def get_last_bid(self, obj):
        last_bid = obj.bids.order_by('-id').first()
        return BidSerializer(last_bid).data if last_bid else None

    def get_bids(self, obj):
        last_bids = obj.bids.order_by('-id')[:10]
        return BidSerializer(last_bids, many=True).data
