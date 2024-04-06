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
            # Store the success message in the session
            request.session['registration_success_message'] = 'Registration successful. Welcome!'
            #messages.success(request, 'Registration successful. Welcome!') #mesajele astea apare in admin interface
            return redirect('/login/')  # Redirect to the home page after successful registration
        else:
            # Form is invalid, so render the form with errors
            #messages.error(request, 'Error in registration. Please correct the form.')
            print(form.errors)  # Print form errors to console for debugging
            return render(request, 'accounts/register.html', {'form': form})   # Pass the form with errors to the template

    else:
        form = RegisterForm()  #daca metoda nu e POST se creaza un empty form 

    return render(request, 'accounts/register.html', {'form': form})


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

    # Check if there is a registration success message in the session
    registration_success_message = request.session.get('registration_success_message')
    if registration_success_message:
        messages.success(request, registration_success_message)
        del request.session['registration_success_message']  # Remove the message from the session after displaying it

    return render(request, 'accounts/login.html', {'form': form})


def home(request):
    return render(request, 'accounts/home.html')


from .models import Income, CashIncome, CardIncome
from .forms import IncomeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

@login_required  # This decorator ensures that only authenticated users can access this view
def income(request):

    total_money = 0

    user_income = Income.objects.filter(user=request.user).last()
    if not user_income:
        # If there is no existing Income instance, create a new one with a total amount of 0
        user_income = Income.objects.create(user=request.user, total_amount=0, currency='USD')

    last_cash_income = CashIncome.objects.filter(income=user_income).last()
    if not last_cash_income:
        last_cash_income = CashIncome.objects.create(income=user_income, amount=0, currency='USD')

    last_card_income = CardIncome.objects.filter(income=user_income).last()
    if not last_card_income:
        last_card_income = CardIncome.objects.create(income=user_income, amount=0, currency='USD')

    total_money = user_income.total_amount   #toti banii din prezent ai userului

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        action = request.POST.get('action')

        if form.is_valid():
            if action == 'compute':
                cash_amount = form.cleaned_data.get('cash_amount') or 0
                card_amount = form.cleaned_data.get('card_amount') or 0
                total_money += cash_amount + card_amount

                last_card_income.amount = card_amount
                last_cash_income.amount = cash_amount
                last_card_income.save()
                last_cash_income.save()

                # Set a session variable to indicate that the form has been computed
                request.session['form_computed'] = True
            
            elif action == 'undo':
                # Check if the form has been computed before allowing undo action
                if request.session.get('form_computed', False):
                    cash_amount = last_cash_income.amount
                    card_amount = last_card_income.amount
                    total_money = total_money - (cash_amount + card_amount)
                
                # Reset the session variable after undoing action
                    request.session['form_computed'] = False

            user_income.total_amount = total_money
            user_income.save()

            # Redirect to prevent form resubmission ----- asta initializeaza si formul
            return HttpResponseRedirect(request.path_info)

            # # Reinitialize the form with empty data
            # form = IncomeForm()

    else:
        form = IncomeForm()

    context = {'form': form, 'total_income': total_money}
    return render(request, 'accounts/income.html', context)





