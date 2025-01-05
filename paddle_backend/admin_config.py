from django.contrib import admin
from Bikes.models import Bikes ,BikeHardware
from Owner.models import OwnerProfile
from Rider.models import UserProfile
from Riderequest.models import Ride_Request
from Trip.models import Trip
from chat.models import ChatRoom, Message

#  all models
admin.site.register(Bikes)
admin.site.register(BikeHardware)
admin.site.register(OwnerProfile)
admin.site.register(UserProfile)  
admin.site.register(Ride_Request)
admin.site.register(Trip)
admin.site.register(ChatRoom)
admin.site.register(Message)