from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re  #re is a built-in Python module that provides support for working with regular expressions. 
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm


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

from .models import Expense
class ExpenseInputForm(forms.ModelForm):  #defined django form class
    #type, frequency, category, and value are fields of the form
    #those are instances of ChoiceField too => allow the user to select a single choice from a list of predefined ones

    #define choices using touples, they are used to render the form but are not directly related to the database schema, so they help in defining the html
    #first val = to store in the database
    #second value = the human-readable label displayed to the user, helps at HTML.
    TYPE_CHOICES = (
        ('essential', 'Essential'),
        ('important', 'Important'),
        ('minor', 'Minor'),
    )

    #These choices are provided using the choices parameter of forms.ChoiceField.
    #this is the name of the field in the form: type
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.RadioSelect) #user can select one option from the available choices by clicking on a radio button.

    FREQUENCY_CHOICES = (
        ('one_time', 'One Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('6_months', 'Every 6 Months'),
        ('yearly', 'Yearly'),
    )
    frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES, widget=forms.RadioSelect)

    CATEGORY_CHOICES = (
        ('housing', 'Housing'),
        ('food', 'Food'),
        ('health', 'Health'),
        ('utilities', 'Utilities'),
        ('transport', 'Transport'),
        ('personal', 'Personal'),
        ('entertainment', 'Entertainment'),
        ('vices', 'Vices'),
        ('other', 'Other'),
    )
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.RadioSelect)

    value = forms.DecimalField(label='Value', max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = Expense
        fields = ['type', 'frequency', 'category', 'value']


from django import forms
from .models import Image

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']


from .models import Goal
class GoalForm(forms.ModelForm):

    class Meta:
        model = Goal
        fields = ['title', 'target_amount']


from django import forms

class SplitIncomeForm(forms.Form):
    economies_amount = forms.DecimalField(label='Amount for Economies', min_value=0, max_digits=10, decimal_places=2, required=False)
    goal_amount = forms.DecimalField(label='Amount for Goal', min_value=0, max_digits=10, decimal_places=2, required=False)

