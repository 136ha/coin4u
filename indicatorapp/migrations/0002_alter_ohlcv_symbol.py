# Generated by Django 4.2.8 on 2024-01-30 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indicatorapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ohlcv',
            name='symbol',
            field=models.CharField(max_length=12),
        ),
    ]