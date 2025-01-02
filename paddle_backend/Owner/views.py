from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view 
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from knox.models import AuthToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from Rider.models import UserProfile
from Owner.serializers import OwnerProfileSerializer, UserProfileSerializer
from django.contrib.auth.decorators import login_required
from knox.views import LogoutAllView
from knox.auth import TokenAuthentication
from django.contrib.auth import logout 
from .models import OwnerProfile


@api_view(['GET']) 
def customer_list(request):
    Owner= UserProfile.objects.all()
    serialized = UserProfileSerializer(Owner, many=True)   
    return JsonResponse(serialized.data, safe=False)


@api_view(['POST'])
def register_Owner(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    phone_number = request.data.get('phone_number')
    cpn = request.data.get('cpn')
    profile_picture = request.data.get('profile_picture')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    elif User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=400)
    try:
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            OwnerProfile.objects.create(user=user,
                                    phone_number=phone_number,
                                    cpn=cpn, 
                                    profile_picture=profile_picture,
                                    latitude=latitude, 
                                    longitude=longitude  
                                    )
            
        return Response({'message': 'Owner registered successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
def Login_Owner(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Authenticate user
    user = authenticate(username=username, password=password)

    if user is not None:
        # Create or retrieve token
        _, token = AuthToken.objects.create(user)
        returninguser = OwnerProfileSerializer(user.userprofile)
        jsondata = returninguser.data
        return Response({'user': {'username':user.username,'email':user.email, 'phone_number' : jsondata['phone_number'] ,'profile_picture': jsondata['profile_picture'], 'token': token} })
    else:
        return Response({'error': 'Invalid credentials'}, status=400)

@api_view(['POST'])
def Logout_Owner(request):
  
    if request.user.is_authenticated:
        # Call Knox's LogoutAllView
        knox_logout_view = LogoutAllView.as_view()
        return knox_logout_view(request._request)
    else:
        return Response({'message': 'User is already logged out'}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@login_required
def update_Owner_profile(request):
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
def delete_Owner_profile(request):
    # Retrieve the UserProfile object for the authenticated user
    user_profile = request.user.userprofile

    # Delete the UserProfile object
    user_profile.delete()
    logout(request)

    return Response({'message': 'User profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@login_required
def search_Owner_profile(request, username):
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