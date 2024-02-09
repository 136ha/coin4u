# Generated by Django 4.2.8 on 2024-02-04 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendarapp', '0010_remove_event_hour_remove_event_quarter_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='epsActual',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='epsEstimate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='epsSurprisePct',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]