from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import DetailView


from .models import *
from .forms import ClientRegistrationForm, CompanyRegistrationForm



def home(request):
    if request.user.is_authenticated:
        if request.user.is_client():
            return redirect('client')  
        elif request.user.is_company():
            return redirect('company') 
        
    login_form = AuthenticationForm(data=request.POST or None)

    if request.method == 'POST':
        if login_form.is_valid(): 
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  
                if user.role == 'client':
                    return redirect('client')  
                elif user.role == 'company':
                    return redirect('company') 
                return redirect('/')  
    return render(request, 'home.html', {'login_form': login_form})



def client_page(request):
    login_form = AuthenticationForm(data=request.POST or None)
    context = {'login_form': login_form}

    if request.user.is_authenticated:
        if request.user.is_client():
            profile = request.user.client_profile
            context.update({
                'name': profile.name,
                'avatar': profile.image.url if profile.image else None
            })
        else:
            context['error_message'] = "Пользователь не клиент."
    else:
        context['error_message'] = "Пользователь не аутентифицирован."
    
    print(context)  # Для отладки — можно убрать потом   
    return render(request, 'client.html', context)  


def company_page(request):
    login_form = AuthenticationForm(data=request.POST or None)
    context = {'login_form': login_form}

    if request.user.is_authenticated:
        if request.user.is_company():
            profile = request.user.company_profile
            context.update({
                'name': profile.company_name,
                'avatar': profile.image.url if profile.image else None,
            })
            buses = Bus.objects.filter(transport_company=profile)
            context.update({
                'buses': buses,
            })
            
            # orders = Order.objects.filter(bus__transport_company=profile).select_related('bus')
            # context.update({
            #     'orders': orders,
            # })
            
            # reviews = Review.objects.filter(bus__transport_company=profile).select_related('bus')
            # context.update({
            #     'reviews': reviews,
            # })
            
            # order_history = orders.filter(status='completed') 
            # context.update({
            #     'order_history': order_history,
            # })
    return render(request, 'company.html', context)


import logging

# Настройка логирования
logger = logging.getLogger(__name__)


def register(request):
    client_form = ClientRegistrationForm(request.POST or None, request.FILES or None, prefix="client")
    company_form = CompanyRegistrationForm(request.POST or None, request.FILES or None, prefix="company")
    login_form = AuthenticationForm(data=request.POST or None)

    if request.method == 'POST':
        logger.info("POST request received with data: %s", request.POST)


        if 'register_client' in request.POST:
            logger.info("Client registration form submitted")
            if client_form.is_valid():
                logger.info("Client form is valid")
                user = client_form.save()
                login(request, user)
                return redirect('client')
            else:
                logger.error("Client form errors: %s", client_form.errors)
                return render(request, 'registration/register.html', {
                    'client_form': client_form,
                    'company_form': company_form,
                    'login_form': login_form
                })


        elif 'register_company' in request.POST:
            logger.info("Company registration form submitted")
            if company_form.is_valid():
                logger.info("Company form is valid")
                user = company_form.save()
                login(request, user)
                return redirect('company')
            else:
                logger.error("Company form errors: %s", company_form.errors)
                return render(request, 'registration/register.html', {
                    'client_form': client_form,
                    'company_form': company_form,
                    'login_form': login_form
                })

    logger.info("GET request or invalid POST")
    return render(request, 'registration/register.html', {
        'client_form': client_form,
        'company_form': company_form,
        'login_form': login_form
    })


class BusDetailView(DetailView):
    model = Bus
    template_name = 'bus_detail.html' 
    context_object_name = 'bus'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bus = self.object
        
        # Разбиваем дополнительные услуги на список
        context['services'] = [service.strip() for service in bus.additional_services.split(',')] if bus.additional_services else []

        return context


def calculate_rental(request):
    if request.method == 'POST':
        bus_id = request.POST.get('bus_id')
        hours = int(request.POST.get('hours'))
        
        bus = Bus.objects.get(id=bus_id)
        total_cost = bus.rental_price_per_hour * hours
        
        return HttpResponse(f'Общая стоимость аренды: {total_cost} руб.') 


@login_required
def add_bus(request):
    if request.method == 'POST' and request.user.is_company():
        company = request.user.company_profile
        name = request.POST.get('name')
        seats = request.POST.get('seats')
        price_per_day = request.POST.get('price_per_day')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')

        Bus.objects.create(
            transport_company=company,
            name=name,
            seats=seats,
            price_per_day=price_per_day,
            description=description,
            image=image
        )
        return redirect('company.html')

