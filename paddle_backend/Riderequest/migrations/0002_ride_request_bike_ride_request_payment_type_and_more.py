# Generated by Django 5.1.4 on 2025-01-17 01:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bikes', '0002_bikehardware_battery_level_bikehardware_factory_key_and_more'),
        ('Riderequest', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride_request',
            name='bike',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ride_requests', to='Bikes.bikes'),
        ),
        migrations.AddField(
            model_name='ride_request',
            name='payment_type',
            field=models.CharField(default='card', max_length=50),
        ),
        migrations.AlterField(
            model_name='ride_request',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ride_request',
            name='requested_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
