from django.contrib.auth.models import User
from Owner.models import OwnerProfile
from Bikes.models import BikeHardware, Bikes
from django.utils import timezone

# Create Users
user1 = User.objects.create_user('owner1', 'owner1@example.com', 'password123')
user2 = User.objects.create_user('owner2', 'owner2@example.com', 'password123')
user3 = User.objects.create_user('owner3', 'owner3@example.com', 'password123')

# Create Owner Profiles
owner1 = OwnerProfile.objects.create(
    user=user1,
    cpn='1234567890123',
    phone_number='+40721111111',
    verification_status='verified'
)

owner2 = OwnerProfile.objects.create(
    user=user2,
    cpn='2234567890123',
    phone_number='+40722222222',
    verification_status='verified'
)

owner3 = OwnerProfile.objects.create(
    user=user3,
    cpn='3234567890123',
    phone_number='+40723333333',
    verification_status='verified'
)

# Create Bike Hardware
hw1 = BikeHardware.objects.create(serial_number='HW001', factory_key='key123', is_assigned=True, battery_level=95)
hw2 = BikeHardware.objects.create(serial_number='HW002', factory_key='key456', is_assigned=True, battery_level=87)
hw3 = BikeHardware.objects.create(serial_number='HW003', factory_key='key789', is_assigned=True, battery_level=92)

# Create Bikes
bike1 = Bikes.objects.create(
    owner=owner1,
    bike_name='City Cruiser',
    brand='Trek',
    model='FX3',
    color='Blue',
    size='M',
    year=2023,
    description='Perfect city bike',
    is_available=True,
    is_active=True,
    bike_status='available',
    latitude=45.74732,
    longitude=21.23135,
    hardware=hw1,
    hardware_status='active'
)

bike2 = Bikes.objects.create(
    owner=owner2,
    bike_name='Mountain Explorer',
    brand='Specialized',
    model='Rockhopper',
    color='Red',
    size='L',
    year=2023,
    description='Great mountain bike',
    is_available=True,
    is_active=True,
    bike_status='available',
    latitude=45.74428,
    longitude=21.20898,
    hardware=hw2,
    hardware_status='active'
)

bike3 = Bikes.objects.create(
    owner=owner3,
    bike_name='Urban Commuter',
    brand='Giant',
    model='Escape',
    color='Black',
    size='M',
    year=2023,
    description='Reliable commuter bike',
    is_available=True,
    is_active=True,
    bike_status='available',
    latitude=45.74705,
    longitude=21.23487,
    hardware=hw3,
    hardware_status='active'
)
