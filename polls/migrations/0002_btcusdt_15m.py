# Generated by Django 4.2.8 on 2023-12-23 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='btcusdt_15m',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('open', models.IntegerField(blank=True, null=True)),
                ('close', models.IntegerField(blank=True, null=True)),
                ('high', models.IntegerField(blank=True, null=True)),
                ('low', models.IntegerField(blank=True, null=True)),
                ('volume', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
