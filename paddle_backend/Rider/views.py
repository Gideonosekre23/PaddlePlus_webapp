from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate, logout
from .models import UserProfile
from Owner.serializers import UserProfileSerializer
from django.contrib.auth.decorators import login_required
# from django.contrib.gis.geos import Point
from django.db import transaction
import stripe

@api_view(['GET']) 
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def Rider_list(request):
    riders = UserProfile.objects.all()
    serialized = UserProfileSerializer(riders, many=True)   
    return JsonResponse(serialized.data, safe=False)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def check_token_validity(request):
    return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_Rider(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    phone_number = request.data.get('phone_number')
    address = request.data.get('address')
    cpn = request.data.get('cpn')
    age = request.data.get('age')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    profile_picture = request.data.get('profile_picture')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    elif User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=400)

    try:
        verification_session = stripe.identity.VerificationSession.create(
            type='document',
            metadata={'email': email, 'cpn': cpn}
        )

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            
            user_profile = UserProfile.objects.create(
                user=user,
                phone_number=phone_number,
                address=address,
                age=age,
                cpn=cpn,
                latitude=latitude,
                longitude=longitude,
                profile_picture=profile_picture,
                verification_status='pending',
                verification_session_id=verification_session.id
            )

            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Registration successful',
                'verification_url': verification_session.url,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': user.id
            })

    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def Login_Rider(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        rider = get_object_or_404(UserProfile, user=user)
        
        if rider.verification_status != 'verified':
            return Response({
                'error': 'Account not verified',
                'verification_status': rider.verification_status
            }, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        returninguser = UserProfileSerializer(rider)
        
        return Response({
            'user': {
                'username': user.username,
                'email': user.email,
                'phone_number': returninguser.data['phone_number'],
                'profile_picture': returninguser.data['profile_picture'],
                'address': returninguser.data['address'],
                'verification_status': rider.verification_status,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        })
    return Response({'error': 'Invalid credentials'}, status=400)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verification_webhook(request):
    event = stripe.Event.construct_from(request.data, stripe.api_key)
    
    if event.type == 'identity.verification_session.verified':
        session = event.data.object
        try:
            rider = UserProfile.objects.get(verification_session_id=session.id)
            rider.verification_status = 'verified'
            rider.save()
            
            return Response({'status': 'verification successful'})
        except UserProfile.DoesNotExist:
            return Response({'error': 'Rider not found'}, status=404)
    
    return Response({'status': 'received'})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def Logout_Rider(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_Rider_profile(request):
    user_profile = request.user.userprofile 
    serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profile updated successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_Rider_profile(request):
    user_profile = request.user.userprofile
    user_profile.delete()
    logout(request)
    return Response({'message': 'User profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def search_Rider_profile(request, username):
    try:
        user = User.objects.get(username=username)
        user_profile = user.userprofile
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_location(request):
    user_profile = request.user.userprofile
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if latitude and longitude:
        user_profile.latitude = float(latitude)
        user_profile.longitude = float(longitude)
        user_profile.save()
        return Response({'status': 'location updated'})
    return Response({'error': 'Invalid data'}, status=400)
