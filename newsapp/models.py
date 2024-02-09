from django.db import models

class Article(models.Model):
    abstract = models.CharField(max_length=200)
    web_url = models.URLField("Site URL", max_length=300, null=True, blank=True)
    snippet = models.CharField(max_length=200, null=True, blank=True)
    lead_paragraph = models.CharField(max_length=200, null=True, blank=True)
    headline = models.JSONField(default=dict, null=True, blank=True)
    keywords = models.JSONField(default=dict, null=True, blank=True)
    pub_date = models.DateTimeField('date published')
    news_desk = models.CharField(max_length=20, null=True, blank=True)
    section_name = models.CharField(max_length=30, null=True, blank=True)
    subsection_name = models.CharField(max_length=20, null=True, blank=True)
    word_count = models.IntegerField(default=0, null=True, blank=True)
    neg = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    neu = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    pos = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return self.pub_date.strftime("%Y-%m-%d") + ' | ' + self.headline['main']
