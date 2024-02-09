from django.db import models
import datetime

# class Event(models.Model):
#     date = models.DateField(null=True)
#     epsActual = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
#     epsEstimate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
#     hour = models.CharField(max_length=5, null=True, blank=True)
#     quarter = models.IntegerField(null=True, blank=True)
#     revenueActual = models.DecimalField(max_digits=20, decimal_places=1, null=True, blank=True)
#     revenueEstimate = models.DecimalField(max_digits=20, decimal_places=1, null=True, blank=True)
#     symbol = models.CharField(max_length=12, null=True)
#
#     def __str__(self):
#         return self.symbol + ' , ' + self.date.strftime("%Y-%m-%d")

class Event(models.Model):
    date = models.DateField(null=True)
    epsActual = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    epsEstimate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    epsSurprisePct = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    symbol = models.CharField(max_length=12, null=True)
    name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.symbol + ' , ' + self.date.strftime("%Y-%m-%d")