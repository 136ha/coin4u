from django.contrib import admin
from .models import Item, Ohlcv

# Register your models here.
admin.site.register(Item)
admin.site.register(Ohlcv)