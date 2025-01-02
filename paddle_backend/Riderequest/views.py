
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Ride_Request
from Owner.serializers import UserProfileSerializer, RideRequestSerializer
from Bikes.models import Bikes
from Owner.models import OwnerProfile
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from push_notifications.models import GCMDevice  
from rest_framework.response import Response
from rest_framework import status
from Trip.models import Trip
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_ride_request(request, request_id):
    try:
        ride_request = Ride_Request.objects.get(pk=request_id, is_accepted=False)
    except Ride_Request.DoesNotExist:
        return Response({'error': 'Ride request not found or already accepted'}, status=status.HTTP_404_NOT_FOUND)
    
    if ride_request.driver is not None:
        return Response({'error': 'Ride request already accepted by another driver'}, status=status.HTTP_400_BAD_REQUEST)

    if ride_request.customer != request.user:
        return Response({'error': 'You are not authorized to accept this ride request'}, status=status.HTTP_403_FORBIDDEN)

    ride_request.accepted_by = request.user.owner_profile  # Correct reference to driver profile
    ride_request.is_accepted = True
    ride_request.save()
    
    bike_current_location = ride_request.bike.current_location
    
    trip = Trip.objects.create(
        renter=ride_request.rider.userprofile,
        bike_owner=request.user.ownerprofile,
        bike=ride_request.bike,
        origin_location=Point(ride_request.pickup_latitude, ride_request.pickup_longitude),
        destination_location=Point(ride_request.destination_latitude, ride_request.destination_longitude),
        distance=ride_request.distance,
        price=ride_request.price,
        duration=ride_request.duration
    )
    
    response_data = {
        'trip_id': trip.id,
        'pickup_location': trip.origin_location,
        'destination': trip.destination_location,
        'bike_current_location': bike_current_location,
        'price': ride_request.price,
        'duration': ride_request.duration,
        'message': 'Ride request accepted successfully'
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decline_ride_request(request, request_id):
    try:
        ride_request = Ride_Request.objects.get(pk=request_id, is_accepted=False)
    except Ride_Request.DoesNotExist:
        return JsonResponse({'error': 'Ride request not found or already accepted'}, status=404)
    
    if ride_request.driver != None:
        return JsonResponse({'error': 'Ride request already accepted by another driver'}, status=400)

    if ride_request.customer != request.user:
        return JsonResponse({'error': ' not authorized '}, status=403)

    device = GCMDevice.objects.get(user=ride_request.customer.user)
    device.send_message("Your ride request has been declined by the driver. Please make a new request.")
    
    ride_request.delete()
    return JsonResponse({'message': 'Ride request declined successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_ride(request):
    pickup_latitude = request.data.get('pickup_latitude')
    pickup_longitude = request.data.get('pickup_longitude')
    destination_latitude = request.data.get('destination_latitude')
    destination_longitude = request.data.get('destination_longitude')
    requested_time = request.data.get('requested_time')
    distance_km = request.data.get('distance_km')
    duration_hours = request.data.get('duration_hours')
    price = request.data.get('price')

    available_bikes = Bike.objects.filter(is_available=True)
    nearby_bikes = available_bikes.annotate(distance=Distance('current_location', Point(pickup_latitude, pickup_longitude))).order_by('distance')

    if not nearby_bikes.exists():
        return Response({'error': 'No available bikes nearby'}, status=status.HTTP_400_BAD_REQUEST)

    nearest_bike = nearby_bikes.first()
    bike_owner = nearest_bike.owner

    device = GCMDevice.objects.get(user=bike_owner.user)
    device.send_message(f"New ride request received from ({pickup_latitude}, {pickup_longitude}) to ({destination_latitude}, {destination_longitude}). Do you want to accept or decline?")
    
    ride_request_data = {
        'customer': request.user.id,
        'pickup_latitude': pickup_latitude,
        'pickup_longitude': pickup_longitude,
        'destination_latitude': destination_latitude,
        'destination_longitude': destination_longitude,
        'requested_time': requested_time,
        'driver': bike_owner.id,
        'price': price,
        'distance': distance_km,
        'duration': duration_hours
    }
    ride_request_serializer = RidesRequestSerializer(data=ride_request_data)
    if ride_request_serializer.is_valid():
        ride_request_serializer.save()

        response_data = {
            'message': 'Ride request created successfully',
            'action_required': 'Please check your notifications to accept or decline the ride request.'
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(ride_request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

