from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .services import PaymentService
from .models import Balance, User
from .serializers import TopUpSerializer, WithdrawSerializer, TransferSerializer
from django.core.exceptions import ValidationError


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def top_up(request):
    """Пополнение счета пользователя"""
    user = request.user
    serializer = TopUpSerializer(data=request.data)

    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        try:
            balance = PaymentService.top_up(user, amount)
            return Response({
                'message': 'Account topped up successfully',
                'balance': balance.balance
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def withdraw(request):
    """Снятие средств с баланса"""
    user = request.user
    serializer = WithdrawSerializer(data=request.data)

    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        try:
            balance = PaymentService.withdraw(user, amount)
            return Response({
                'message': 'Withdrawal successful',
                'balance': balance.balance
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def transfer(request):
    """Перевод средств между пользователями"""
    user = request.user
    serializer = TransferSerializer(data=request.data)

    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        receiver_username = serializer.validated_data['receiver_username']
        try:
            receiver = User.objects.get(username=receiver_username)
            sender_balance, receiver_balance = PaymentService.transfer(user, receiver, amount)
            return Response({
                'message': 'Transfer successful',
                'sender_balance': sender_balance.balance,
                'receiver_balance': receiver_balance.balance
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_balance(request):
    """Получение текущего баланса пользователя"""
    user = request.user
    try:
        balance = PaymentService.get_user_balance(user)
        return Response({
            'balance': balance.balance
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)