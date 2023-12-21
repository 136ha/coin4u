import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone



class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class btcusdt_15m(models.Model):
    timestamp = models.DateTimeField(auto_now=True, null=True, blank=True)
    open = models.IntegerField(blank=True, null=True)
    close = models.IntegerField(blank=True, null=True)
    high = models.IntegerField(blank=True, null=True)
    low = models.IntegerField(blank=True, null=True)
    volume = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.timestamp)