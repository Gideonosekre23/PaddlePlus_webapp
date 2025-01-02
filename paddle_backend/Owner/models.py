from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator

class OwnerProfile(models.Model):
    user = models.OneToOneField(User, related_name='owner_profile', on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="owner/profile/")
    cpn = models.CharField(max_length=13, validators=[MinLengthValidator(13), MaxLengthValidator(13)])
    phone_number = models.CharField(max_length=15)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)  
    longitude = models.FloatField(null=True, blank=True)