from .forms import RegisterForm, LoginForm #from forms.py
from django.contrib import messages 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate #for user login
from django.contrib.auth import login as auth_login  # Import Django's authenticate and login function


def register(request):
    if request.method == 'POST':  #request for submision, it means that the user has submitted the registration form, then a register form with the submited data will be initialized 
        form = RegisterForm(request.POST) #processes the form data, and performs registration logic based on whether the form is valid or not.
        if form.is_valid():  #daca registerform are totul in regula => creaza userul in baza de date django admin
            # user = form.save()  # Save the user to the database
            form.save()
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

from django.utils import timezone
from .models import Income, CashIncome, CardIncome

@login_required
def income(request):
    total_money = 0
    now = timezone.now()
    month = now.month
    year = now.year

    user_income = Income.objects.filter(user=request.user, month=month, year=year).last()

    if not user_income:
        user_income = Income.objects.create(user=request.user, total_amount=0, income_left=0, month=month, year=year)

    last_cash_income = CashIncome.objects.filter(income=user_income).last()
    if not last_cash_income:
        last_cash_income = CashIncome.objects.create(income=user_income, amount=0, currency='USD')

    last_card_income = CardIncome.objects.filter(income=user_income).last()
    if not last_card_income:
        last_card_income = CardIncome.objects.create(income=user_income, amount=0, currency='USD')

    total_money = user_income.total_amount
    total_left = user_income.income_left

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        action = request.POST.get('action')

        if form.is_valid():
            if action == 'compute':
                cash_amount = form.cleaned_data.get('cash_amount') or 0
                card_amount = form.cleaned_data.get('card_amount') or 0

                total_money += cash_amount + card_amount
                total_left += cash_amount + card_amount

                last_card_income.amount = card_amount
                last_cash_income.amount = cash_amount
                last_card_income.save()
                last_cash_income.save()

                CashIncome.objects.create(income=user_income, amount=cash_amount, currency='USD')
                CardIncome.objects.create(income=user_income, amount=card_amount, currency='USD')

                request.session['form_computed'] = True
            
            elif action == 'undo':
                if request.session.get('form_computed', False):
                    cash_amount = last_cash_income.amount
                    card_amount = last_card_income.amount
                    total_money = total_money - (cash_amount + card_amount)
                    total_left = total_left - (cash_amount + card_amount)
                    request.session['form_computed'] = False

            user_income.total_amount = total_money
            user_income.income_left = total_left
            user_income.save()

            return HttpResponseRedirect(request.path_info)

    else:
        form = IncomeForm()

    context = {'form': form, 'total_income': total_money}
    return render(request, 'accounts/income.html', context)


@login_required
def income_details(request):
    cash_incomes = CashIncome.objects.filter(income__user=request.user, amount__gt=0).order_by('-day', '-hour') #income__user is essentially telling Django to follow the ForeignKey relationship from CashIncome or CardIncome to the Income model, and then from the Income model to the User model, allowing us to filter incomes based on the user they belong to.
    card_incomes = CardIncome.objects.filter(income__user=request.user, amount__gt=0).order_by('-day', '-hour')
    return render(request, 'accounts/income_details.html', {'cash_incomes': cash_incomes, 'card_incomes': card_incomes})


from .models import Expense, TotalExpense
from .forms import ExpenseInputForm
from decimal import Decimal


@login_required
def create_expense(request):
    now = timezone.now()
    month = now.month
    year = now.year

    # Check if TotalExpense object for the current month and year exists
    total_expense, created = TotalExpense.objects.get_or_create(
        user=request.user,
        month=month,
        year=year,
        defaults={
            'total_housing_expense': 0,
            'total_food_expense': 0,
            'total_health_expense': 0,
            'total_utilities_expense': 0,
            'total_transport_expense': 0,
            'total_personal_expense': 0,
            'total_entertainment_expense': 0,
            'total_vices_expense': 0,
            'total_other_expense': 0,
            'total_expenses': 0
        }
    )


    if request.method == 'POST':
        print("POST")
        form = ExpenseInputForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            # Set the user for the expense based on the current user
            expense.user = request.user
            # Save the expense object to the database
            expense.save()

            income = Income.objects.get(user=request.user)
            income.income_left = income.income_left - expense.value
            income.save()
            # Update total expenses
            update_total_expenses(request.user, month, year)

            return HttpResponseRedirect(request.path_info)
            #return redirect('expense_list')  # Redirect to a page showing the list of expenses
    
    elif request.method == 'GET':
        print("GET")
        total_amount = request.GET.get('total_amount2')
        print("1 Total Amount:", total_amount)
        total_amount = Decimal(total_amount) if total_amount else None
        print("2 Total Amount:", total_amount)
        form = ExpenseInputForm(initial={'value': total_amount})

    # Get total expenses for the current user
    total_expenses = TotalExpense.objects.get(user=request.user, month=month, year=year)

    print(total_expenses)
    
    return render(request, 'accounts/expense.html', {'form': form, 'total_expenses': total_expenses})

from django.utils import timezone

def update_total_expenses(user, month, year):
    # Get all expenses of the user from database for the specified month and year
    user_expenses = Expense.objects.filter(user=user, day__month=month, day__year=year)
    # Initialize total expense for each category
    total_expenses = {
        'housing': 0,
        'food': 0,
        'health': 0,
        'utilities': 0,
        'transport': 0,
        'personal': 0,
        'entertainment': 0,
        'vices': 0,
        'other': 0,
    }

    # Calculate total expenses for each category
    for expense in user_expenses:
        total_expenses[expense.category] += expense.value

    # Check if TotalExpense object already exists for the user, month, and year
    total_expense, created = TotalExpense.objects.get_or_create(
        user=user,
        month=month,
        year=year,
        defaults={
            'total_housing_expense': 0,
            'total_food_expense': 0,
            'total_health_expense': 0,
            'total_utilities_expense': 0,
            'total_transport_expense': 0,
            'total_personal_expense': 0,
            'total_entertainment_expense': 0,
            'total_vices_expense': 0,
            'total_other_expense': 0,
            'total_expenses': 0
        }
    )
    
    # Update individual expense fields
    total_expense.total_housing_expense = total_expenses['housing']
    total_expense.total_food_expense = total_expenses['food']
    total_expense.total_health_expense = total_expenses['health']
    total_expense.total_utilities_expense = total_expenses['utilities']
    total_expense.total_transport_expense = total_expenses['transport']
    total_expense.total_personal_expense = total_expenses['personal']
    total_expense.total_entertainment_expense = total_expenses['entertainment']
    total_expense.total_vices_expense = total_expenses['vices']
    total_expense.total_other_expense = total_expenses['other']

    # Update total expenses field
    total_expense.update_total_expenses()



import requests
from django.shortcuts import render, redirect
from .forms import ImageForm
import json
import os

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image
            image_uploaded = form.save()
            #Get the URL of the uploaded image
            image_url = image_uploaded.image.url
            image_url = request.build_absolute_uri(image_uploaded.image.url)

            # ocr_api_key = os.getenv('OCR_API_KEY')
            
            # # Call the OCR API with the image URL
            # receipt_ocr_endpoint = 'https://ocr.asprise.com/api/v1/receipt'
            # payload = {
            #     'api_key': ocr_api_key,
            #     'recognizer': 'auto',
            # }
            # files = {"file": requests.get(image_url).content}
            # r = requests.post(receipt_ocr_endpoint, data=payload, files=files)
            # ocr_result = r.json()

            # Store JSON response in a file
            # with open('ocr_result.json', 'w') as json_file:
            #     json.dump(ocr_result, json_file)

            with open('ocr_result.json', 'r') as f:
                data = json.load(f)

            # Extract necessary information
            items = data['receipts'][0]['items']
            currency = data['receipts'][0]['currency']
            total_amount = data['receipts'][0]['total']
            total_amount2 = data['receipts'][0]['total']
            print(total_amount2, "...........................")

            # Format items and amounts
            formatted_data = []
            for item in items:
                formatted_item = f"{item['description']}   {item['amount']}{currency} "
                formatted_data.append(formatted_item)

            # Construct a line of dots
            separator = '*' * 40
            
            return render(request, 'accounts/upload_image.html', {'formatted_data': formatted_data, 'separator': separator, 'total_amount': f"{total_amount}{currency} " , 'total_amount2': total_amount2})

    else:
        form = ImageForm()
    return render(request, 'accounts/upload_image.html', {'form': form})


from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import GoalForm
from .models import Goal
from django.contrib.auth.decorators import login_required

@login_required
def create_goal(request):
    # Check if there are any existing goals for the user
    existing_goals = Goal.objects.filter(user=request.user)
    
    if existing_goals.exists():
        # Check if any existing goals have not been achieved
        unachieved_goals_exist = existing_goals.filter(achieved=False).exists()
        if unachieved_goals_exist:
            # If there are unachieved goals, prevent the user from creating a new one
            return HttpResponse("You cannot create a new goal until the previous one is achieved.")
    
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            # Save the goal to the database
            goal = form.save(commit=False)
            goal.user = request.user  # Assign the current user to the goal
            goal.save()
            #return redirect('/see_goals/')  # Redirect to the detail page of the created goal
    else:
        form = GoalForm()
        
    return render(request, 'accounts/goal.html', {'form': form})



from .models import Goal
def all_goals(request):
    # Retrieve all goals from the database
    goals = Goal.objects.filter(user=request.user)  # Assuming each goal is associated with a user
    return render(request, 'accounts/all_goals.html', {'goals': goals})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SplitIncomeForm
from .models import Income, Economies, Goal, GoalSavings
from datetime import datetime, timedelta

# @login_required
# def split_income(request):
#     user = request.user
#     now = datetime.now()
#     month = now.month
#     year = now.year

#     if month == 1:  # If the current month is January, adjust the year and month
#         last_month = 12  # December
#         year -= 1  # Subtract 1 from the current year
#     else:
#         last_month = month - 1

#     last_month_income = Income.objects.filter(user=user, month=last_month, year=year).first()

#     if request.method == 'POST':
#         form = SplitIncomeForm(request.POST)
#         if form.is_valid():
#             monthly_economies = form.cleaned_data['monthly_economies']
#             monthly_savings = form.cleaned_data['monthly_savings']

#             # Create or update Economies object
#             Economies.create_or_update_economies(user=user, month=last_month, year=year, monthly_economies=monthly_economies)

#             # Get or create the user's savings goal for the previous month
#             goal, created = Goal.objects.get_or_create(user=user)
#             # Create or update GoalSavings object
#             GoalSavings.create_or_update_goal_savings(goal=goal, month=last_month, year=year, monthly_savings=monthly_savings)

#             return redirect('dashboard')  # Redirect to the user's dashboard after splitting income
#     else:
#         form = SplitIncomeForm()

#     return render(request, 'split_income.html', {'last_month_income': last_month_income, 'form': form})




from django.shortcuts import render
from django.http import HttpResponse
from django.template import TemplateDoesNotExist  # Import TemplateDoesNotExist
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to test OpenAI API key
def test_openai_api_key(request):
    # Get API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        return HttpResponse("Error: OpenAI API key not found in environment variables.")

    # Create OpenAI client instance with API key
    client = OpenAI(api_key=api_key)

    # Test API key by calling a simple API method
    try:
        # Call OpenAI API with a simple message and specify the model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a budgeting analyst."},
                {"role": "user", "content": "how to maximize my savings?"}
            ],
            max_tokens=100  # Adjust the maximum number of tokens as needed
        )
        
        # Accessing the completion text from the response
        completion_text = response.choices[0].message.content
        
        # Render a template with the completion text
        try:
            return render(request, 'accounts/openai_result.html', {'completion_text': completion_text})
        except TemplateDoesNotExist as e:
            return HttpResponse("Error: TemplateDoesNotExist - " + str(e))
    except Exception as e:
        return HttpResponse("Error: " + str(e) + ". API key is not working.")


#ASTA MERGE, ITI RASPUNDE LA FIECARE CHESTIE DIN CHAT, TREBUIE SA VAD CUM IL FAC SA FIE CHAT FARA SA ISI DEA RESET PAGINA 

from django.shortcuts import render

# Assuming you have already imported other necessary modules and classes

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
conversation = []  # Initialize an empty list to store conversation messages

def chat_view(request):
    
    if request.method == 'POST':
        user_input = request.POST.get('message')
        if user_input:
            # Append user message to conversation
            conversation.append({"role": "user", "content": user_input})
            
            # Create the OpenAI client
            client = OpenAI(api_key=OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a budgeting analyst."},
                    {"role": "user", "content": user_input}
                ]
            )
            # Append AI response to conversation
            conversation.append({"role": "assistant", "content": completion.choices[0].message.content})
    
    return render(request, 'accounts/chat.html', {'conversation': conversation})



from .forms import SplitIncomeForm  # Import your form class here

@login_required
def split_income(request):
    user = request.user
    now = datetime.now()
    month = now.month
    year = now.year

    if month == 1:
        last_month = 12
        year -= 1
    else:
        last_month = month - 1

    last_month_income = Income.objects.filter(user=user, month=last_month, year=year).last()

    if request.method == 'POST':
        form = SplitIncomeForm(request.POST)
        if form.is_valid():
            economies_amount_raw = form.cleaned_data['economies_amount']
            goal_amount_raw = form.cleaned_data['goal_amount']
            economies_amount = Decimal(str(economies_amount_raw)).quantize(Decimal('0.01'))
            goal_amount = Decimal(str(goal_amount_raw)).quantize(Decimal('0.01'))
            print(economies_amount)
            print(goal_amount)

            # Calculate remaining income after splitting
            remaining_income = last_month_income.income_left
            remaining_income -= Decimal(economies_amount)
            remaining_income -= Decimal(goal_amount)
            last_month_income.income_left=remaining_income
            last_month_income.save()

            # Save the split income to the respective models
            economies = Economies.create_or_update_economies(
                user=user,
                month=last_month,
                year=year,
                monthly_economies=economies_amount
            )
            print(economies.monthly_economies)

            goal = Goal.objects.filter(user=user).last()
            if goal.achieved==False:
                goal_savings = GoalSavings.create_or_update_goal_savings(
                    goal=goal,
                    month=last_month,
                    year=year,
                    monthly_savings=goal_amount
                )
                print(goal_savings.monthly_savings)

                # Check if the goal has been achieved
                goal_savings.total_savings += Decimal(goal_amount)
                if goal_savings.total_savings >= goal.target_amount:
                    goal.achieved = True
                    goal.save()
            
    else:
        form = SplitIncomeForm()

    return render(request, 'accounts/split_income.html', {'last_month_income': last_month_income, 'form': form})









