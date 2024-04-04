from .forms import RegisterForm, LoginForm #from forms.py
from django.contrib import messages 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate #for user login
from django.contrib.auth import login as auth_login  # Import Django's authenticate and login function

def register(request):
    if request.method == 'POST':  #request for submision, it means that the user has submitted the registration form, then a register form with the submited data will be initialized 
        form = RegisterForm(request.POST) #processes the form data, and performs registration logic based on whether the form is valid or not.
        if form.is_valid():  #daca registerform are totul in regula => creaza userul in baza de date django admin
            user = form.save()  # Save the user to the database
            # Automatically create an income for the new user with default values
            income = Income.objects.create(user=user, total_amount=0, currency='USD')
            # Optionally, you can set other default values for the income object here
            income.save()
            messages.success(request, 'Registration successful. Welcome!') #mesajele astea apare in admin interface
            return redirect('/login/')  # Redirect to the home page after successful registration
        else:
            # Form is invalid, so render the form with errors
            messages.error(request, 'Error in registration. Please correct the form.')
            print(form.errors)  # Print form errors to console for debugging
            return render(request, 'accounts/register.html', {'form': form})   # Pass the form with errors to the template

    else:
        form = RegisterForm()  #daca metoda nu e POST se creaza un empty form 

    return render(request, 'accounts/register.html', {'form': form})


# def login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             auth_login(request, user)  # Use Django's login function with the alias
#             return redirect('/home/')  # redirect to home page only if they are logged in 
#         else:
#             messages.error(request, 'Invalid username or password.')

#     return render(request, 'accounts/login.html')

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Form is valid, attempt to authenticate the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']  # Match your form field name
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # User authenticated successfully, log in the user
                auth_login(request, user)
                messages.success(request, 'Login successful.')  # Display success message
                return redirect('/home/')  # Redirect to the home page after login
            else:
                # Authentication failed, display error message
                messages.error(request, 'Invalid username or password.')
                print(form.errors)  # Print form errors to console for debugging
                return render(request, 'accounts/login.html', {'form': form})   # Pass the form with errors to the template
    else:
        form = LoginForm()  # Create a new instance of the LoginForm
    return render(request, 'accounts/login.html', {'form': form})


def home(request):
    return render(request, 'accounts/home.html')

from .models import Income
from .forms import IncomeForm
from django.contrib.auth.decorators import login_required

@login_required  # This decorator ensures that only authenticated users can access this view
def income(request):
    total_income = 0
    user_income = Income.objects.filter(user=request.user).last()  # This variable represents the latest Income object associated with the current user;  

    if user_income:
        total_income = user_income.total_amount #If there is an existing income record for the user, user_income will hold that record; otherwise, it will be None.

    if request.method == 'POST':  #daca avem date de trm la server atunci mergem pe ramura asta 
        form = IncomeForm(request.POST) #request.POST to access form data introduced by user.
        if form.is_valid():
            cash_amount = form.cleaned_data.get('cash_amount') or 0  # Get cash amount from form or default to 0;     cleaned_data iti da datele bune introduse de user dupa validare
            card_amount = form.cleaned_data.get('card_amount') or 0  # Get card amount from form or default to 0

            # Calculate total_income based on provided amounts
            total_income += cash_amount + card_amount

            # Update the total_amount in the database for the current user
            if user_income:
                user_income.total_amount = total_income
                user_income.save()
            else:
                user_income = Income.objects.create(user=request.user, total_amount=total_income, currency='USD')

            # Reset the form to empty after successful submission
            form = IncomeForm()  # Reinitialize the form with empty values

    else:
        form = IncomeForm()

    context = {'form': form, 'total_income': total_income}  #The context is a way to pass data to the template ('accounts/income.html') when rendering it.
    return render(request, 'accounts/income.html', context)

