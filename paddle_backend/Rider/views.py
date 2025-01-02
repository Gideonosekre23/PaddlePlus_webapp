from datetime import timedelta
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from django.contrib.auth import authenticate
from .models import UserProfile
from Owner.serializers import UserProfileSerializer
from django.contrib.auth.decorators import login_required
from knox.views import LogoutAllView 
from django.contrib.gis.geos import Point
from django.contrib.auth import logout 
from django.db import transaction

@api_view(['GET']) 
def Rider_list(request):
    Rider = UserProfile.objects.all()
    serialized = UserProfileSerializer(Rider, many=True)   
    return JsonResponse(serialized.data, safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_token_validity(request):
    try:
        # If the request reaches this point, the token is valid
        return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)
    except AuthenticationFailed as e:
        # Handle the case where the token is invalid or expired
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle any other exceptions
        return Response({'error': 'An unexpected error occurred: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    profile_picture = request.data.get('picture_picture')



    # Check if the username or email already exists
    if User.objects.filter(username=username).exists():
       return Response({'error': 'Username already exists'}, status=400)
    elif User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=400)
    try:
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)

            # Create the user profile
            UserProfile.objects.create(
                user=user,
                phone_number=phone_number,
                address=address,
                age=age,
                cpn=cpn,
                latitude=latitude,
                longitude=longitude,
                profile_picture=profile_picture
            )
        return Response({'message': 'User registered successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def Login_Rider(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Authenticate user
    user = authenticate(username=username, password=password)

    if user is not None:
        # Create or retrieve token
        expiry = timedelta(minutes=30)
        _, token = AuthToken.objects.create(user, expiry=expiry)
        returninguser = UserProfileSerializer(user.userprofile)
        jsondata = returninguser.data
        return Response({'user ': {'username':user.username,'email':user.email, 'phone_number' : jsondata['phone_number'] ,'profile_picture': jsondata['profile_picture'], 'address': jsondata['address'], 'token': token} })
    else:
        return Response({'error': 'Invalid credentials'}, status=400)

@api_view(['POST'])
def Logout_Rider(request):
  
    if request.user.is_authenticated:
        # Call Knox's LogoutAllView
        knox_logout_view = LogoutAllView.as_view()
        return knox_logout_view(request._request)
    else:
        return Response({'message': 'User is already logged out'}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@login_required
def update_Rider_profile(request):
    # get the UserProfile object for the authenticated user
    user_profile = request.user.userprofile 

    data = request.data

    # Serialize the data received in the request
    serializer = UserProfileSerializer(user_profile, data=data, partial= True)

    # Validate and save the updated data
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profile updated successfully'})
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@login_required
def delete_Rider_profile(request):
    # Retrieve the UserProfile object for the authenticated user
    user_profile = request.user.userprofile

    # Delete the UserProfile object
    user_profile.delete()
    logout(request)

    return Response({'message': 'User profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@login_required
def search_Rider_profile(request, username):
    try:
        # Retrieve the user based on the provided username
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve the UserProfile object for the user
    user_profile = user.userprofile

    # Serialize the UserProfile object
    serializer = UserProfileSerializer(user_profile)

    return Response(serializer.data)


@api_view(['POST'])
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
    else:
        return Response({'error': 'Invalid data'}, status=400)
        return Response({'error': 'Invalid data'}, status=400)