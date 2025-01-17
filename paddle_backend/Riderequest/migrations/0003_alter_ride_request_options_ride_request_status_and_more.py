# Generated by Django 5.1.4 on 2025-01-17 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bikes', '0002_bikehardware_battery_level_bikehardware_factory_key_and_more'),
        ('Owner', '0001_initial'),
        ('Rider', '0001_initial'),
        ('Riderequest', '0002_ride_request_bike_ride_request_payment_type_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ride_request',
            options={'ordering': ['-requested_time']},
        ),
        migrations.AddField(
            model_name='ride_request',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.AddIndex(
            model_name='ride_request',
            index=models.Index(fields=['status', 'requested_time'], name='Riderequest_status_b2b626_idx'),
        ),
        migrations.AddIndex(
            model_name='ride_request',
            index=models.Index(fields=['Rider', 'status'], name='Riderequest_Rider_i_95bd60_idx'),
        ),
        migrations.AddIndex(
            model_name='ride_request',
            index=models.Index(fields=['Owner', 'status'], name='Riderequest_Owner_i_79c343_idx'),
        ),
    ]
