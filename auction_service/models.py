from django.db import models
from user_service.models import Profile 

class Lot(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_reserve = models.BooleanField(default=False)
    reserve_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='lots')

    def __str__(self):
        return f"{self.title} (by {self.seller.user.username})"

class Bid(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of {self.amount} by {self.bidder.user.username} on {self.lot.title}"