from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('username', email.split('@')[0])

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password=password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Клиент'),
        ('company', 'Транспортная компания'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    email = models.EmailField(unique=True, verbose_name='Email')
    username = models.CharField(max_length=150, blank=True, null=True)  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  
    objects = UserManager() 

    def is_client(self):
        return self.role == 'client'

    def is_company(self):
        return self.role == 'company'




class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    STATUS = (
        ('legal_entity', 'Юридическое лицо'),
        ('individual', 'Физическое лицо'),
    )
    email = models.EmailField(unique=True, verbose_name='Почта')
    status = models.CharField(max_length=20, choices= STATUS, verbose_name='Cтатус')
    name = models.CharField(max_length=20, verbose_name= 'Имя клиента или организации')
    image = models.ImageField(upload_to='avatar_client/', null=True, blank= True, default= None, verbose_name='Аватарка')

    def __str__(self):
        return self.name



class TransportCompany(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255, help_text="Название транспортной компании")
    email = models.EmailField(unique=True, verbose_name='Почта')
    STATUS = (
        ('legal_entity', 'Юридическое лицо'),
        ('individual', 'Физическое лицо'),
    )
    status = models.CharField(max_length=20, choices= STATUS, verbose_name='Cтатус')
    image = models.ImageField(upload_to='avatar_company/', null=True, blank= True, default= None, verbose_name='Аватарка')
    TIN = models.CharField(max_length=20, null=True, blank=True, verbose_name='ИНН компании')
    description = models.TextField(null=True, blank=True, verbose_name='Описание компании')

    def __str__(self):
        return self.company_name
    

class Comfort(models.Model):
    comforts_choices = [
        ('wi_fi', 'Wi-Fi'),
        ('air_conditioning', 'Кондиционер'),
        ('tv', 'Телевизор'),
        ('toilet', 'Туалет'),
        ('reclining_seats', 'Откидывающиеся сиденья'),
        ('charging_ports', 'Зарядные порты'),
    ]
    name = models.CharField(max_length=100, choices= comforts_choices, default= 'Нет удобств', verbose_name="Удобство")
    image = models.ImageField(upload_to='comforts/', verbose_name="Изображение", blank=True, null=True)
    def __str__(self):
        return self.name  
    

class Bus(models.Model):
    transport_company = models.ForeignKey(TransportCompany, on_delete=models.CASCADE, related_name="buses", verbose_name="Транспортная Компания")
    name = models.CharField(max_length=100, verbose_name="Название автобуса")
    photo = models.ImageField(upload_to='bus_photos/', null=True, blank=True, verbose_name="Фото автобуса")
    description = models.TextField(default="Пока нет описания", verbose_name="Описание")
    seats_count = models.PositiveIntegerField(default=0, blank=True, verbose_name="Количество мест")
    comforts = models.ManyToManyField(Comfort, verbose_name="Удобства")
    # Дополнительные услуги (можно использовать ту же логику, что и выше)
    additional_services = models.TextField(verbose_name="Дополнительные услуги", blank=True)
    rental_price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Цена аренды за 1 час")
    
    def __str__(self):
        return f"{self.name} ({self.seats_count} мест)"
 


