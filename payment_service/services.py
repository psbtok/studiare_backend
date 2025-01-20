from django.db import transaction
from .models import Balance, Transaction
from django.core.exceptions import ValidationError

class PaymentService:

    @staticmethod
    def top_up(user, amount):
        """Пополнение баланса пользователя."""
        if amount <= 0:
            raise ValidationError("Amount must be positive.")
        
        balance, created = Balance.objects.get_or_create(user=user)
        balance.balance += amount
        balance.save()

        Transaction.objects.create(
            sender=None, 
            receiver=user,
            type='topup',
            amount=amount
        )
        return balance

    @staticmethod
    def withdraw(user, amount):
        """Снятие средств с баланса пользователя."""
        if amount <= 0:
            raise ValidationError("Amount must be positive.")
        
        balance = Balance.objects.get(user=user)
        if balance.balance < amount:
            raise ValidationError("Insufficient balance.")

        balance.balance -= amount
        balance.save()

        Transaction.objects.create(
            sender=user,
            receiver=None,  
            type='withdrawal',
            amount=amount
        )
        return balance

    @staticmethod
    def transfer(sender, receiver, amount):
        """Перевод средств с одного пользователя на другого."""
        if amount <= 0:
            raise ValidationError("Amount must be positive.")
        
        if sender == receiver:
            raise ValidationError("Sender and receiver cannot be the same.")

        sender_balance = Balance.objects.get(user=sender)
        receiver_balance, created = Balance.objects.get_or_create(user=receiver)
        if sender_balance.balance < amount:
            raise ValidationError("Insufficient balance.")
        
        with transaction.atomic():  
            sender_balance.balance -= amount
            receiver_balance.balance += amount
            sender_balance.save()
            receiver_balance.save()

        Transaction.objects.create(
            sender=sender,
            receiver=receiver,
            type='transfer',
            amount=amount
        )
        return sender_balance, receiver_balance
    
    @staticmethod
    def get_user_balance(user):
        """Получение текущего баланса пользователя."""
        balance, created = Balance.objects.get_or_create(user=user, defaults={'balance': 0})
        return balance
