# Generated by Django 4.2.8 on 2024-01-27 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_alter_question_pub_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('symbol', models.CharField(max_length=12)),
                ('open', models.IntegerField(blank=True, null=True)),
                ('close', models.IntegerField(blank=True, null=True)),
                ('high', models.IntegerField(blank=True, null=True)),
                ('low', models.IntegerField(blank=True, null=True)),
                ('volume', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='btcusd',
        ),
        migrations.AddField(
            model_name='question',
            name='long',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='short',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='sideway',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.CharField(max_length=20),
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
    ]
