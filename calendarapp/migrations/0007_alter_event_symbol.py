# Generated by Django 4.2.8 on 2024-01-27 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendarapp', '0006_alter_event_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='symbol',
            field=models.CharField(max_length=12, null=True),
        ),
    ]
