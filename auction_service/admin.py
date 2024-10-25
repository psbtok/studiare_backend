from django.contrib import admin
from .models import Lot, Bid

@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'seller', 'starting_price', 'is_reserve', 'reserve_price', 'start_datetime', 'end_datetime')
    search_fields = ('title', 'seller__username')
    list_filter = ('is_reserve', 'start_datetime', 'end_datetime')
    ordering = ('start_datetime',)

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'lot', 'bidder', 'amount', 'datetime')
    search_fields = ('lot__title', 'bidder__username')