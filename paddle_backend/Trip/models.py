from django.db import models
from django.contrib.auth.models import User
from Rider.models import UserProfile 
from Owner.models import OwnerProfile  
from Bikes.models import Bikes 


class Trip(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('waiting', 'Waiting'),
        ('started', 'Started'),
        ('canceled', 'Canceled'),
        ('ontrip', 'On Trip'),
        ('completed', 'Completed'),
    ]

    renter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='trips_taken')
    bike_owner = models.ForeignKey(OwnerProfile, on_delete=models.CASCADE, related_name='trips_given')
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    trip_date = models.DateTimeField(auto_now_add=True)
    origin_latitude = models.FloatField(null=True, blank=True)
    origin_longitude = models.FloatField(null=True, blank=True)
    destination_latitude = models.FloatField(null=True, blank=True)
    destination_longitude = models.FloatField(null=True, blank=True)
    origin_map = models.ImageField(upload_to='trip_maps/', null=True, blank=True)
    destination_map = models.ImageField(upload_to='trip_maps/', null=True, blank=True)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=100)
    trip_canceled = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')

    def __str__(self):
        return f"Trip #{self.pk} from ({self.origin_latitude}, {self.origin_longitude}) to ({self.destination_latitude}, {self.destination_longitude})"


