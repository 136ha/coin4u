# Generated by Django 4.2.8 on 2024-03-02 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indicatorapp', '0009_remove_financialstatement_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialstatement',
            name='year',
            field=models.CharField(default=None, max_length=4),
            preserve_default=False,
        ),
    ]
