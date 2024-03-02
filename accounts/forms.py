from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Create a username (only letters and numbers)', 
        'required': 'True'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your first name', 
        'required': 'True'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your last name', 
        'required': 'True'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email address', 
        'required': 'True'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Create a password', 
        'required': 'True'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password', 
        'required': 'True'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')