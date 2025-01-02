from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Trip
from Bikes.models import Bikes
import stripe
from geopy.distance import geodesic

# Initialize Stripe API with your API key
stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_trip(request, trip_id):
    try:
        trip = Trip.objects.get(pk=trip_id, renter=request.user.userprofile)
    except Trip.DoesNotExist:
        return JsonResponse({'error': 'Trip not found or you are not authorized'}, status=404)

    if trip.status != 'created':
        return JsonResponse({'error': 'Trip cannot be started'}, status=400)

    # Set trip status to 'started'
    trip.status = 'started'
    trip.save()

    return JsonResponse({'message': 'Trip started successfully'})

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_trip(request, trip_id):
    try:
        trip = Trip.objects.get(pk=trip_id, renter=request.user.userprofile)
    except Trip.DoesNotExist:
        return JsonResponse({'error': 'Trip not found or you are not authorized'}, status=404)

    if trip.status == 'completed':
        return JsonResponse({'error': 'Trip already completed'}, status=400)

    # Set trip status to 'canceled'
    trip.status = 'canceled'
    trip.save()

    return JsonResponse({'message': 'Trip canceled successfully'})

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_trip(request, trip_id):
    try:
        trip = Trip.objects.get(pk=trip_id, renter=request.user.userprofile)
    except Trip.DoesNotExist:
        return JsonResponse({'error': 'Trip not found or you are not authorized'}, status=404)

    if trip.status != 'ontrip':
        return JsonResponse({'error': 'Trip cannot be ended'}, status=400)

    # Calculate total price for the trip
    if trip.distance is None:
        origin_coords = (trip.origin_latitude, trip.origin_longitude)
        destination_coords = (trip.destination_latitude, trip.destination_longitude)
        trip.distance = geodesic(origin_coords, destination_coords).kilometers
        trip.save()

    total_price = trip.price  # Assuming price is already calculated and stored in the trip model

    try:
        # Create a charge using Stripe API
        charge = stripe.Charge.create(
            amount=int(total_price * 100),  # Convert price to cents
            currency='usd',
            source=request.data.get('token'),  # Payment token from frontend
            description='Trip payment',
        )

        # Payment successful, set trip status to 'completed'
        trip.status = 'completed'
        trip.save()

        return JsonResponse({'message': 'Trip ended successfully'})
    except stripe.error.CardError as e:
        # Card error occurred, increment payment attempts and save to trip
        trip.payment_attempts += 1
        trip.save()
        
        # Check if maximum payment attempts reached
        if trip.payment_attempts >= settings.MAX_PAYMENT_ATTEMPTS:
            # Maximum attempts reached, set trip status to 'payment_failed'
            trip.status = 'payment_failed'
            trip.save()
            return JsonResponse({'error': str(e), 'message': 'Maximum payment attempts reached'}, status=400)
        else:
            # Return error response with card error message
            return JsonResponse({'error': str(e), 'message': f'Payment attempt {trip.payment_attempts} failed, please try again'}, status=400)
    except Exception as e:
        # Other errors occurred, return error response
        return JsonResponse({'error': str(e)}, status=500)

