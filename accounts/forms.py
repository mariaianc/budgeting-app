from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re  #re is a built-in Python module that provides support for working with regular expressions. 
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

# class LoginForm(AuthenticationForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs.update({'placeholder': 'Enter your username'})
#         self.fields['password'].widget.attrs.update({'placeholder': 'Enter your password'})

from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your username',  # Updated placeholder text
        'required': 'True'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',  # Updated placeholder text
        'required': 'True'
    }))

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username doesn\'t exist.')
        return username

    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data['password']
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None or not user.check_password(password):
                raise forms.ValidationError('Incorrect password.')
        return password

    

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

    #for cleaning and validating the username field of the form.
    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^(?=.*[a-zA-Z])[a-zA-Z0-9]+$', username):
            raise ValidationError('Username must contain at least one letter and can only contain letters and numbers.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username is already taken, choose anotherone.')
        return username
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[A-Z][a-z]+$', first_name):
            raise ValidationError('First name must start with an uppercase letter and contain only letters.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[A-Z][a-z]+$', last_name):
            raise ValidationError('Last name must start with an uppercase letter and contain only letters.')
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email field is required.')
        # if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        #     raise ValidationError('Please enter a valid email address.')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email is used in another account.')
        return email
    

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        errors = []
        errors.append('Password must be at least 8 characters long.''\n')
        errors.append('Password must contain at least one letter.''\n')
        errors.append('Password must contain at least one digit.''\n')
        errors.append('Password must contain at least one special character.''\n')
        if len(password1) < 8:
            raise ValidationError(errors)
        if not re.search(r'[a-zA-Z]', password1):
            raise ValidationError(errors)
        if not re.search(r'\d', password1):
            raise ValidationError(errors)
        if not re.search(r'[^a-zA-Z0-9]', password1):
            raise ValidationError(errors)
        return password1
    
    def clean_password2(self):
        # password1 = self.cleaned_data.get('password1')
        password1 = self.data.get('password1')  # Access raw data directly          CUM FAC SA NU IMI APARA ALTE MESAJE DE EROARE AICI????????????
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        return password2

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


from decimal import Decimal, ROUND_DOWN
class IncomeForm(forms.Form):
    cash_amount = forms.DecimalField(label='Cash Amount', max_digits=10, decimal_places=2, required=False)  #required=False allows the user to leave these fields empty if they only want to input cash or card but not both.
    card_amount = forms.DecimalField(label='Card Amount', max_digits=10, decimal_places=2, required=False)
    
    #in case if the user enter 2 instead of decimal 2.00, the app will convert it to decimal
    def clean_cash_amount(self):
        cash_amount = self.cleaned_data.get('cash_amount')
        if cash_amount is not None:
            cash_amount = Decimal(str(cash_amount)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        return cash_amount

    def clean_card_amount(self):
        card_amount = self.cleaned_data.get('card_amount')
        if card_amount is not None:
            card_amount = Decimal(str(card_amount)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        return card_amount