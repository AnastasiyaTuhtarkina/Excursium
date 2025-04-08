from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Client, TransportCompany

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']


class ClientRegistrationForm(UserRegistrationForm):
    status = forms.ChoiceField(
        choices=Client.STATUS,
        widget=forms.Select(attrs={'class': 'form-select', 'aria-label': 'Статус'})
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя клиента или организации'})
    )
    image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))

    class Meta(UserRegistrationForm.Meta):
        fields = UserRegistrationForm.Meta.fields + ['status', 'name', 'image']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        user.username = self.cleaned_data['email'] 
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                email=user.email,
                status=self.cleaned_data['status'],
                name=self.cleaned_data['name'],
                image=self.cleaned_data.get('image'),
            )
        return user



class CompanyRegistrationForm(UserRegistrationForm):
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название компании'})
    )
    status = forms.ChoiceField(
        choices=TransportCompany.STATUS,
        widget=forms.Select(attrs={'class': 'form-select', 'aria-label': 'Статус компании'})
    )
    image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))
    TIN = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ИНН компании'}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Описание компании'}),
    )

    class Meta(UserRegistrationForm.Meta):
        fields = UserRegistrationForm.Meta.fields + ['company_name', 'status', 'image', 'TIN', 'description']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'company'
        user.username = self.cleaned_data['email'] 
        if commit:
            user.save()
            TransportCompany.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                email=user.email,
                status=self.cleaned_data['status'],
                image=self.cleaned_data.get('image'),
                TIN=self.cleaned_data.get('TIN'),
                description=self.cleaned_data.get('description'),
            )
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
