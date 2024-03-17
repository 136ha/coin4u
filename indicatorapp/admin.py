from django.contrib import admin
from .models import Ohlcv, USBureauEvent, FinancialStatement

class OhlcvAdmin(admin.ModelAdmin):
    search_fields = ['symbol']

# Register your models here.
admin.site.register(Ohlcv, OhlcvAdmin)
admin.site.register(USBureauEvent)
admin.site.register(FinancialStatement)