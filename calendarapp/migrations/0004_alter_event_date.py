# Generated by Django 4.2.8 on 2024-01-27 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendarapp', '0003_alter_event_epsactual_alter_event_epsestimate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.CharField(max_length=12, null=True),
        ),
    ]