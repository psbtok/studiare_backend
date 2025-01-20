from rest_framework import serializers

class TopUpSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1, required=True)

class WithdrawSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1, required=True)

class TransferSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1, required=True)
    receiver_username = serializers.CharField(max_length=150, required=True)
