from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import *

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    # path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_bus/', add_bus, name='add_bus'),
    path('client/', views.client_page, name='client'), 
    path('company/', views.company_page, name='company'),
    path('bus/<int:pk>/', BusDetailView.as_view(), name='bus_detail'),
    path('calculate_rental/', calculate_rental, name='calculate_rental'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)