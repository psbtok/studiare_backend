from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance', null=False)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"Balance for {self.user.username}: {self.balance}"



class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('topup', 'Top-up'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_transactions', on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_transactions', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction from {self.sender} to {self.receiver} of {self.amount}"
