from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

# python manage.py shell

# python manage.py makemigrations
# python manage.py migrate

class User(AbstractUser):
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_room = models.ForeignKey('Room', on_delete=models.CASCADE)

class Room(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='photos/')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    first_data = models.DateField()
    last_data = models.DateField()

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    title = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='photos/')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)

class AdminPanel(models.Model):
    confirmation = models.BooleanField(default=False)
    cancel_reservations = models.BooleanField(default=False)
    edit_booking = models.BooleanField(default=False)
    delete_booking = models.BooleanField(default=False)

class Calendar(models.Model):
    free_rooms = models.BooleanField(default=True)
    busy_rooms = models.BooleanField(default=False)
    filter_by_date = models.DateField()

class AddEditRoom(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    add_room = models.BooleanField(default=False)
    edit_room = models.BooleanField(default=False)
    delete_information_room = models.BooleanField(default=False)
    delete_room = models.BooleanField(default=False)
