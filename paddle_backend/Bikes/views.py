from django.shortcuts import render

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from Owner.models import OwnerProfile  
from customers.serializers import BikesSerializer
from .models import Bikes
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from Trip.models import Trip
from geopy.distance import geodesic
from .pricing import calculate_price

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def add_bike(request):
    if request.user.is_authenticated and hasattr(request.user, 'owner_profile'):
        Owner_profile = request.user.owner_profile
        data = request.data.copy()
        data['owner'] = owner_profile.id

        serializer = BikesSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            bikes = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Only authenticated Owner can add bikes.'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def get_Owner_bikes(request):
    try:
        # Retrieve the driver profile from the authenticated user
        owner_profile = request.user.owner_profile
    except OwnerProfile.DoesNotExist:
        return Response({'error': 'Owner profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve the bikes associated with the driver's profile
    bikes = Bikes.objects.filter(owner=driver_profile)
    
    # Serialize the bike data
    serializer = BikesSerializer(bikes, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def make_bike_available(request, bike_id):
    # Check if the user is authenticated and is a driver
    if request.user.is_authenticated and hasattr(request.user, 'owner_profile'):
        try:
            # Retrieve the bike associated with the provided bike_id
            bike = Bikes.objects.get(pk=bike_id, owner=request.user.owner_profile)
        except Bikes.DoesNotExist:
            return Response({'error': 'Bike not found or you are not the owner'}, status=status.HTTP_404_NOT_FOUND)

        # Update the is_available field to True
        bike.is_available = True
        bike.save()

        return Response({'message': 'Bike is now available'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Only authenticated drivers can make bikes available'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def get_available_bikes(request):
    latitude = request.query_params.get('latitude')
    longitude = request.query_params.get('longitude')

    if not (latitude and longitude):
        return Response({'error': 'Latitude and longitude parameters are required'}, status=400)

    user_location = (float(latitude), float(longitude))
    search_radius_km = 5  # Define the search radius in kilometers

    bikes = Bikes.objects.filter(is_available=True)
    nearby_bikes = []

    for bike in bikes:
        if bike.latitude is not None and bike.longitude is not None:
            bike_location = (bike.latitude, bike.longitude)
            distance = geodesic(user_location, bike_location).kilometers
            if distance <= search_radius_km:
                bike.distance = distance  # Add distance attribute for sorting
                nearby_bikes.append(bike)

    nearby_bikes.sort(key=lambda x: x.distance)

    serializer = BikeSerializer(nearby_bikes, many=True)
    return Response(serializer.data)







@api_view(['POST'])
def search_for_ride(request):
    # Get customer's latitude and longitude from the request data
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if not (latitude and longitude):
        return Response({'error': 'Latitude and longitude are required'}, status=400)

    customer_location = (float(latitude), float(longitude))

    # Define the search radius (in kilometers)
    search_radius_km = 5  # Adjust the search radius as needed

    # Query all available bikes
    available_bikes = Bike.objects.filter(is_available=True)
    nearby_bikes = []

    for bike in available_bikes:
        if bike.latitude is not None and bike.longitude is not None:
            bike_location = (bike.latitude, bike.longitude)
            distance = geodesic(customer_location, bike_location).kilometers
            if distance <= search_radius_km:
                bike.distance = distance  # Add distance attribute for sorting
                nearby_bikes.append(bike)

    nearby_bikes.sort(key=lambda x: x.distance)

    if nearby_bikes:
        # Calculate price for the ride
        distance_km = request.data.get('distance_km')
        duration_hours = request.data.get('duration_hours')
        base_fare = 5  # Define your base fare
        rate_per_km = 2  # Define your rate per kilometer
        rate_per_hour = 1.5  # Define your rate per hour

        # Call the calculate_price function to get the total fare
        price = calculate_price(distance_km, duration_hours, base_fare, rate_per_km, rate_per_hour)

        # Serialize the data and return available bikes along with price
        serializer = BikeSerializer(nearby_bikes, many=True)
        return Response({'available_bikes': serializer.data, 'price': price})
    else:
        # Check for partially available bikes (e.g., bikes that will become available soon)
        partially_available_trips = Trip.objects.filter(status='ontrip')
        partially_available_bikes = []
        
        for trip in partially_available_trips:
            destination_location = (trip.destination_latitude, trip.destination_longitude)
            distance_to_destination = geodesic(customer_location, destination_location).kilometers
            if distance_to_destination <= search_radius_km * 0.1:  # e.g., within 10% of the search radius
                partially_available_bikes.append(trip.bike)
        
        if partially_available_bikes:
            return Response({'message': 'Bike available soon (90% done trip)'})
        else:
            return Response({'message': 'No available bikes at the moment'})
