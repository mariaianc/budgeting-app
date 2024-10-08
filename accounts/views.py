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
            #print("Form errors:", form.errors)
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
            # # Authentication failed, display error message
            # messages.error(request, 'Invalid username or password.')
            # print(form.errors)  # Print form errors to console for debugging
            return render(request, 'accounts/login.html', {'form': form})   # Pass the form with errors to the template
    else:
        form = LoginForm()  # Create a new instance of the LoginForm

    # # Check if there is a registration success message in the session
    # registration_success_message = request.session.get('registration_success_message')
    # if registration_success_message:
    #     messages.success(request, registration_success_message)
    #     del request.session['registration_success_message']  # Remove the message from the session after displaying it

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


#vad daca o integrez in frontend sau o sterg complet, verifica cash si card ca se salveaza de 2 ori

# @login_required
# def income_details(request):
#     cash_incomes = CashIncome.objects.filter(income__user=request.user, amount__gt=0).order_by('-day', '-hour') #income__user is essentially telling Django to follow the ForeignKey relationship from CashIncome or CardIncome to the Income model, and then from the Income model to the User model, allowing us to filter incomes based on the user they belong to.
#     card_incomes = CardIncome.objects.filter(income__user=request.user, amount__gt=0).order_by('-day', '-hour')
#     return render(request, 'accounts/income_details.html', {'cash_incomes': cash_incomes, 'card_incomes': card_incomes})


from .models import Expense, TotalExpense
from .forms import ExpenseInputForm
from decimal import Decimal


@login_required
def create_expense(request):
    now = timezone.now()
    month = now.month
    year = now.year

    # Check if TotalExpense object for the current month and year exists          , created langa total expense
    total_expense= TotalExpense.objects.get_or_create(
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
        #print("POST")
        form = ExpenseInputForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)   #necesar ca userul sa nu fie null, altfel primesti eroare
            # Set the user for the expense based on the current user
            expense.user = request.user
            # Save the expense object to the database
            expense.save()

            income = Income.objects.get(user=request.user, month = month) # problema cu luatul unui sg income din baza de date
            income.income_left = income.income_left - expense.value
            income.save()
            # Update total expenses
            update_total_expenses(request.user, month, year)

            return HttpResponseRedirect(request.path_info)
            #return redirect('expense_list')  # Redirect to a page showing the list of expenses
    
    elif request.method == 'GET':
        #print("GET")
        total_amount = request.GET.get('total_amount2')
        #print("1 Total Amount:", total_amount)
        total_amount = Decimal(total_amount) if total_amount else ""
        #print("2 Total Amount:", total_amount)
        form = ExpenseInputForm(initial={'value': total_amount})

    # Get total expenses for the current user
    total_expense = TotalExpense.objects.get(user=request.user, month=month, year=year)

    print(total_expense)
    
    return render(request, 'accounts/expense.html', {'form': form, 'total_expenses': total_expense})

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

    # Calculate total expenses for each category si le stribuie dictionarului de sus
    for expense in user_expenses:
        total_expenses[expense.category] += expense.value

    # Check if TotalExpense object already exists for the user, month, and year; vede daca are obiect de total expenses asociat, daca nu at il creeaza
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
            #  r = requests.post(receipt_ocr_endpoint, data=payload, files=files)
            #  ocr_result = r.json()

            # #Store JSON response in a file
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


#tot pt frontend
# from .models import Goal
# def all_goals(request):
#     # Retrieve all goals from the database
#     goals = Goal.objects.filter(user=request.user)  # Assuming each goal is associated with a user
#     return render(request, 'accounts/all_goals.html', {'goals': goals})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SplitIncomeForm
from .models import Income, Economies, Goal, GoalSavings
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.template import TemplateDoesNotExist  # Import TemplateDoesNotExist
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


#numa pt testare cheie
# # Function to test OpenAI API key
# def test_openai_api_key(request):
#     # Get API key from environment variables
#     api_key = os.getenv("OPENAI_API_KEY")
#     if api_key is None:
#         return HttpResponse("Error: OpenAI API key not found in environment variables.")

#     # Create OpenAI client instance with API key
#     client = OpenAI(api_key=api_key)

#     # Test API key by calling a simple API method
#     try:
#         # Call OpenAI API with a simple message and specify the model
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo-0125",
#             messages=[
#                 {"role": "system", "content": "You are a budgeting analyst."},
#                 {"role": "user", "content": "how to maximize my savings?"}
#             ],
#             max_tokens=100  # Adjust the maximum number of tokens as needed
#         )
        
#         # Accessing the completion text from the response
#         completion_text = response.choices[0].message.content
        
#         # Render a template with the completion text
#         try:
#             return render(request, 'accounts/openai_result.html', {'completion_text': completion_text})
#         except TemplateDoesNotExist as e:
#             return HttpResponse("Error: TemplateDoesNotExist - " + str(e))
#     except Exception as e:
#         return HttpResponse("Error: " + str(e) + ". API key is not working.")


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
# ca sa mearga mai bine, sa pun datele in baza de date pt ultima luna la economies ca sa se vada totalu pana at
@login_required
def split_income(request):
    user = request.user
    user2 = request.user
    now = datetime.now()
    month = now.month
    year = now.year

    if month == 1:
        last_month = 12
        year -= 1
    else:
        last_month = month - 1

    last_month_income = Income.objects.filter(user=user, month=last_month, year=year).last()

    try:
        total_economies_last = Economies.objects.get(user=user, month = last_month-1).total_economies
    except Economies.DoesNotExist:
        total_economies_last = 0

    try:
        latest_goal_savings = GoalSavings.objects.filter(goal__user=user, month = last_month-1).latest('id')
        total_goal_savings_last = latest_goal_savings.total_savings
    except GoalSavings.DoesNotExist:
        total_goal_savings_last = 0


    recommendation1 = ""  # Initialize with default value
    recommendation2 = ""  # Initialize with default value

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
            economies.total_economies = total_economies_last + economies_amount
            economies.save()
            print(economies.monthly_economies)
            print(economies.total_economies)

            goal = Goal.objects.filter(user=user).last()
            if goal.achieved==False:
                goal_savings = GoalSavings.create_or_update_goal_savings(
                    goal=goal,
                    month=last_month,
                    year=year,
                    monthly_savings=goal_amount
                )
                goal_savings.total_savings = total_goal_savings_last + goal_amount
                goal_savings.save()
                print(goal_savings.monthly_savings)

                # Check if the goal has been achieved
                # goal_savings.total_savings += Decimal(goal_amount)
                if goal_savings.total_savings >= goal.target_amount:
                    goal.achieved = True
                    goal.save()

            # total_economies = Economies.objects.get(user=user, month = last_month).total_economies
            total_economies = economies.total_economies
            total_goal_savings = goal_savings.total_savings
            # latest_goal_savings = GoalSavings.objects.filter(goal__user=user, month = last_month).latest('id')
            # total_goal_savings = latest_goal_savings.total_savings
            
    else:
        form = SplitIncomeForm()


        # Query updated total_economies and total_goal_savings
        try:
            latest_economies = Economies.objects.filter(user=user).latest('id')
            total_economies = latest_economies.total_economies
        except Economies.DoesNotExist:
            total_economies = 0

        try:
            latest_goal_savings = GoalSavings.objects.filter(goal__user=user).latest('id')
            total_goal_savings = latest_goal_savings.total_savings
        except GoalSavings.DoesNotExist:
            total_goal_savings = 0

    recommendation1 = generate_recommendation_numeric(user2)  
    recommendation2 = generate_recommendation_fuzzy(user2)

    # recommendation1 = "prima"
    # recommendation2 = "a doua"

    
    return render(request, 'accounts/split_income.html', {'last_month_income': last_month_income, 'form': form, 'recommendation1': recommendation1, 'recommendation2': recommendation2, 'total_economies': total_economies, 'total_goal_savings': total_goal_savings})

def generate_recommendation_numeric(user):
    print(user)
    now = datetime.now()
    month = now.month
    year = now.year

    if month == 1:
        last_month = 12
        year -= 1
    else:
        last_month = month - 1

    last_month_income = Income.objects.filter(user=user, month=last_month, year=year).last()   
    total_income = last_month_income.total_amount
    left_income = last_month_income.income_left

    last_month_total_expenses = TotalExpense.objects.filter(user=user, month=last_month, year=year).last() 
    total_expenses = last_month_total_expenses.total_expenses
    housing = last_month_total_expenses.total_housing_expense
    food = last_month_total_expenses.total_food_expense
    health = last_month_total_expenses.total_health_expense
    utilities = last_month_total_expenses.total_utilities_expense
    transport = last_month_total_expenses.total_transport_expense
    personal = last_month_total_expenses.total_personal_expense
    entertainment = last_month_total_expenses.total_entertainment_expense
    vices = last_month_total_expenses.total_vices_expense
    other = last_month_total_expenses.total_other_expense

    goal = Goal.objects.filter(user=user).last()
    goal_name = goal.title
    cost = goal.target_amount

    goal_savings = GoalSavings.create_or_update_goal_savings(
    goal=goal,
    month=last_month,
    year=year,
    monthly_savings=0)

    savings = goal_savings.total_savings


    economies = Economies.create_or_update_economies(
    user=user,
    month=last_month,
    year=year,
    monthly_economies=0)
    total_economies = economies.total_economies
    

    user_input = f""" Here is my financial data from the last month:
    About Income:
    Total Income (after taxes): {total_income}
    Leftover Income at the End of the Month: {left_income}

    About Expenses:
    Total Expenses: {total_expenses}
    Expenses Breakdown:
    - Housing: {housing}
    - Food: {food}
    - Health: {health}
    - Utilities: {utilities}
    - Transport: {transport}
    - Personal: {personal}
    - Entertainment: {entertainment}
    - Vices: {vices}
    - Other: {other}

    Goal Savings:
        - Total Savings: {savings}
        - Target Amount: {cost}

    Emergency Fund Balance: {total_economies} 

    Respond to the following questions with specific recommendations:
    1. How should I split my leftover income between the Emergency Fund and my Goal Fund? Give me the concrete values to put in each fund based on the leftover income.(the leftover income has to be split completely between emergency and goal funds)
    2. Are there any specific categories where I can reduce expenses without impacting my quality of life?
    3. How can I create a budget plan to better manage my monthly income and expenses next month?
    """

    system_content = """
    You are a financial advisor into a budgeting app tasked with analyzing the user's financial data and providing tailored recommendations to optimize their budget and achieve their financial goals.
    Consider the user's priorities, such as building an Emergency Fund, making progress towards their savings goal, and reducing unnecessary expenses.
    Your main objectives are to provide concrete allocation strategies for the user's leftover income, identify potential areas for expense reduction without compromising their quality of life, and offer guidance on creating a budget plan for better financial management next month.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_input}
    ],
    # max_tokens=500,
    temperature = 0.3 #cea mai buna pt chestii stiintifice si precise,ne creative
    )

    recommendation = completion.choices[0].message.content

    return recommendation
    

def generate_recommendation_fuzzy(user):
    # Obtain user's financial data
    now = datetime.now()
    month = now.month
    year = now.year

    if month == 1:
        last_month = 12
        year -= 1
    else:
        last_month = month - 1

    last_month_income = Income.objects.filter(user=user, month=last_month, year=year).last()
    total_income = float(last_month_income.total_amount)
    left_income = float(last_month_income.income_left)

    last_month_total_expenses = TotalExpense.objects.filter(user=user, month=last_month, year=year).last()
    total_expenses = float(last_month_total_expenses.total_expenses)
    housing = float(last_month_total_expenses.total_housing_expense)
    food = float(last_month_total_expenses.total_food_expense)
    health = float(last_month_total_expenses.total_health_expense)
    utilities = float(last_month_total_expenses.total_utilities_expense)
    transport = float(last_month_total_expenses.total_transport_expense)
    personal = float(last_month_total_expenses.total_personal_expense)
    entertainment = float(last_month_total_expenses.total_entertainment_expense)
    vices = float(last_month_total_expenses.total_vices_expense)
    other = float(last_month_total_expenses.total_other_expense)

    goal = Goal.objects.filter(user=user).last()
    goal_name = goal.title
    cost = float(goal.target_amount)

    goal_savings = GoalSavings.create_or_update_goal_savings(
        goal=goal,
        month=last_month,
        year=year,
        monthly_savings=0)
    savings = float(goal_savings.total_savings)

    economies = Economies.create_or_update_economies(
        user=user,
        month=last_month,
        year=year,
        monthly_economies=0)
    total_economies = float(economies.total_economies)

    # Calculate membership degrees for each category
    income_membership_dict = income_membership(total_income)
    left_income_membership_dict = left_income_membership(left_income)

    total_expenses_membership_dict = total_expenses_membership(total_expenses, total_income)

    housing_membership_dict = housing_membership(housing, total_income)
    food_membership_dict = food_membership(food, total_income)
    health_membership_dict = health_membership(health, total_income)
    utilities_membership_dict = utilities_membership(utilities, total_income)
    transport_membership_dict = transport_membership(transport, total_income)
    personal_membership_dict = personal_membership(personal, total_income)
    entertainment_membership_dict = entertainment_membership(entertainment, total_income)
    vices_membership_dict = vices_membership(vices, total_income)
    other_membership_dict = other_membership(other, total_income)

    total_economies_membership_dict = emergency_fund_membership(total_income, total_economies)

    goal_membership_dict = goal_membership(savings, cost)

    user_input = f""" 
    Here is my financial data from the last month:
    Interpretation: The highest membership value indicates the category where the entitie is situated: high, medium or low.
        About Income:
        Total Income (after taxes): {total_income} (Membership: High: {income_membership_dict['high']}, Medium: {income_membership_dict['medium']}, Low: {income_membership_dict['low']})
        Leftover Income at the End of the Month: {left_income} (Membership: High: {left_income_membership_dict['high']}, Medium: {left_income_membership_dict['medium']}, Low: {left_income_membership_dict['low']})
        If leftover income is high it means that the user saved a lot that month and if it is low that means the user don't save much that month.

        About Expenses:
        Total Expenses: {total_expenses} (Membership: High: {total_expenses_membership_dict['high']}, Medium: {total_expenses_membership_dict['medium']}, Low: {total_expenses_membership_dict['low']})
        Membership of total expenses are computed in tersm of the income so if the total expenses are high it means the user spends too much and if they are low or medium it means the user spending behaviour is good for maximizing the savings.
        Expenses Breakdown:
        - Housing: {housing} (Membership: High: {housing_membership_dict['high']}, Medium: {housing_membership_dict['medium']}, Low: {housing_membership_dict['low']})
        - Food: {food} (Membership: High: {food_membership_dict['high']}, Medium: {food_membership_dict['medium']}, Low: {food_membership_dict['low']})
        - Health: {health} (Membership: High: {health_membership_dict['high']}, Medium: {health_membership_dict['medium']}, Low: {health_membership_dict['low']})
        - Utilities: {utilities} (Membership: High: {utilities_membership_dict['high']}, Medium: {utilities_membership_dict['medium']}, Low: {utilities_membership_dict['low']})
        - Transport: {transport} (Membership: High: {transport_membership_dict['high']}, Medium: {transport_membership_dict['medium']}, Low: {transport_membership_dict['low']})
        - Personal: {personal} (Membership: High: {personal_membership_dict['high']}, Medium: {personal_membership_dict['medium']}, Low: {personal_membership_dict['low']})
        - Entertainment: {entertainment} (Membership: High: {entertainment_membership_dict['high']}, Medium: {entertainment_membership_dict['medium']}, Low: {entertainment_membership_dict['low']})
        - Vices: {vices} (Membership: High: {vices_membership_dict['high']}, Medium: {vices_membership_dict['medium']}, Low: {vices_membership_dict['low']})
        - Other: {other} (Membership: High: {other_membership_dict['high']}, Medium: {other_membership_dict['medium']}, Low: {other_membership_dict['low']})
        If the category is high that means the user spend much on that and if it is low it means the user did not spend much money on it. In the categories "Housing", "Food", "Health", "Utilities" is ok to spend high but on the others is best to tend to low/medium.

        Emergency Fund: {total_economies}
        Emergency Fund Membership: (Membership: High: {total_economies_membership_dict['high']}, Medium: {total_economies_membership_dict['medium']}, Low: {total_economies_membership_dict['low']})
        The emergency membership is medium or low when the user has to continue to invest over time to build the fund and high when the user can invest lower amounts in it because the funds are enough.

        Goal Savings:
        - Total Savings: {savings}
        - Target Amount: {cost}
        - Goal Progress Membership: High: {goal_membership_dict['high']}, Medium: {goal_membership_dict['medium']}, Low: {goal_membership_dict['low']}
        The goal progress membership is medium or high when the target is almost achived and low when the user has to continue to invest.

        Respond to the following questions with specific recommendations, take into account membership functions used for each question:
        1. How should I split my leftover income between the Emergency Fund and my Goal Fund? Give me the concrete values to put in each fund based on the leftover income. (the leftover income has to be split completely between emergency and goal funds) 
        2. Are there any specific categories where I can reduce expenses without impacting my quality of life?
        3. How can I create a budget plan to better manage my monthly income and expenses next month?
        """

    system_content = """
        You are a financial advisor into a budgeting app tasked with analyzing the user's financial data and providing tailored recommendations to optimize their budget and achieve their financial goals.
        Consider the user's priorities, such as building an Emergency Fund, making progress towards their savings goal, and reducing unnecessary expenses.
        Your main objectives are to provide concrete allocation strategies for the user's leftover income, identify potential areas for expense reduction without compromising their quality of life, and offer guidance on creating a budget plan for better financial management next month.
        Put accent on the membership functions and explain to the user what are those and how to improve its financial life based on those.
        """



    # Generate recommendation using OpenAI API
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input}
        ],
        # max_tokens=500,
        temperature = 0.3
    )

    recommendation = completion.choices[0].message.content

    # return formatted_response
    return recommendation



# Import the triangular_sigmoid function from the fuzzylogic library
from fuzzylogic.functions import triangular_sigmoid

# Define a function to determine the membership of an income value in different income categories
def income_membership(income):
    """
    Determine the membership of an income value in the categories: high, medium, low.
    
    Args:
    - income (float): The income value.
    
    Returns:
    - dict: A dictionary showing the percentage of income belonging to each category.
    """
    
    # Define membership functions for income categories using triangular_sigmoid
    high_income = triangular_sigmoid(70000, 149132)  # Example income ranges for high income
    medium_income = triangular_sigmoid(50000, 89744)  # Example income ranges for medium income
    low_income = triangular_sigmoid(0, 55000)  # Example income ranges for low income
    
    # Calculate membership degrees for each income category
    membership_high = high_income(income)
    membership_medium = medium_income(income)
    membership_low = low_income(income)
    
    # Create a dictionary to store the percentages of income belonging to each category
    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }
    
    # Return the dictionary
    return membership_dict

def left_income_membership(left_income):
    """
    Determine the membership of an income left value (savings) in the categories: high, medium, low.
    
    Args:
    - left_income (float): The income left value (savings) after expenses.
    
    Returns:
    - dict: A dictionary showing the percentage of income left belonging to each category.
    """
    
    # Define membership functions for left income categories using triangular_sigmoid
    high_left_income = triangular_sigmoid(0.7 * 70000, 149132)  # Adjusted for high income
    medium_left_income = triangular_sigmoid(0.4 * 50000, 0.7 * 89744)  # Adjusted for medium income
    low_left_income = triangular_sigmoid(0, 0.4 * 55000)  # Adjusted for low income
    
    # Calculate membership degrees for each left income category
    membership_high_left = high_left_income(left_income)
    membership_medium_left = medium_left_income(left_income)
    membership_low_left = low_left_income(left_income)
    
    # Create a dictionary to store the percentages of left income belonging to each category
    membership_dict = {
        'high': membership_high_left,
        'medium': membership_medium_left,
        'low': membership_low_left
    }
    
    # Return the dictionary
    return membership_dict

#expense raportat la income
def total_expenses_membership(expenses, income):
   
    high_expenses = triangular_sigmoid(0.7 * income, income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.4 * income, 0.7 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.4 * income)  # Adjusted for low income

    # Calculate membership degrees for each expense category
    membership_high = high_expenses(expenses)
    membership_medium = medium_expenses(expenses)
    membership_low = low_expenses(expenses)

    # Create a dictionary to store the percentages of expenses belonging to each income category
    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }
    
    # Return the dictionary
    return membership_dict

def housing_membership(housing_expense, income):
    high_expenses = triangular_sigmoid(0.3 * income, 0.4 * income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.1 * income, 0.2 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.05 * income)  # Adjusted for low income

    # Calculate membership degrees for each expense category
    membership_high = high_expenses(housing_expense)
    membership_medium = medium_expenses(housing_expense)
    membership_low = low_expenses(housing_expense)

    # Create a dictionary to store the percentages of expenses belonging to each income category
    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

def food_membership(food_expense, income):
    high_expenses = triangular_sigmoid(0.1 * income, 0.2 * income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.05 * income, 0.1 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.05 * income)  # Adjusted for low income

    membership_high = high_expenses(food_expense)
    membership_medium = medium_expenses(food_expense)
    membership_low = low_expenses(food_expense)

    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

def health_membership(health_expense, income):
    high_expenses = triangular_sigmoid(0.05 * income, 0.1 * income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.02 * income, 0.05 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.02 * income)  # Adjusted for low income

    membership_high = high_expenses(health_expense)
    membership_medium = medium_expenses(health_expense)
    membership_low = low_expenses(health_expense)

    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

def utilities_membership(utilities_expense, income):
    high_expenses = triangular_sigmoid(0.05 * income, 0.1 * income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.02 * income, 0.05 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.02 * income)  # Adjusted for low income

    membership_high = high_expenses(utilities_expense)
    membership_medium = medium_expenses(utilities_expense)
    membership_low = low_expenses(utilities_expense)

    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

def transport_membership(transport_expense, income):
    high_expenses = triangular_sigmoid(0.05 * income, 0.1 * income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.02 * income, 0.05 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.02 * income)  # Adjusted for low income

    membership_high = high_expenses(transport_expense)
    membership_medium = medium_expenses(transport_expense)
    membership_low = low_expenses(transport_expense)

    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

def personal_membership(personal_expense, income):
    high_expenses = triangular_sigmoid(0.05 * income, 0.1 * income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.02 * income, 0.05 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.02 * income)  # Adjusted for low income

    membership_high = high_expenses(personal_expense)
    membership_medium = medium_expenses(personal_expense)
    membership_low = low_expenses(personal_expense)

    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

def entertainment_membership(entertainment_expense, income):
    high_expenses = triangular_sigmoid(0.03 * income, 0.08 * income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.01 * income, 0.03 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.01 * income)  # Adjusted for low income

    membership_high = high_expenses(entertainment_expense)
    membership_medium = medium_expenses(entertainment_expense)
    membership_low = low_expenses(entertainment_expense)

    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

def vices_membership(vices_expense, income):
    high_expenses = triangular_sigmoid(0.02 * income, 0.05 * income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.01 * income, 0.02 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.01 * income)  # Adjusted for low income

    membership_high = high_expenses(vices_expense)
    membership_medium = medium_expenses(vices_expense)
    membership_low = low_expenses(vices_expense)

    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

def other_membership(other_expense, income):
    high_expenses = triangular_sigmoid(0.02 * income, 0.05 * income)  # Adjusted for high income
    medium_expenses = triangular_sigmoid(0.01 * income, 0.02 * income)  # Adjusted for medium income
    low_expenses = triangular_sigmoid(0, 0.01 * income)  # Adjusted for low income

    membership_high = high_expenses(other_expense)
    membership_medium = medium_expenses(other_expense)
    membership_low = low_expenses(other_expense)

    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict

# def total_economies_membership(total_economies):
    """
    Calculate the membership degrees for the emergency fund based on the total amount accumulated over time.

    Args:
    - total_economies (float): Total amount accumulated in the emergency fund over time.

    Returns:
    - dict: A dictionary containing the membership degrees for high, medium, and low emergency fund.
    """
    # Define the ranges for high, medium, and low emergency fund based on the total amount accumulated
    high_economies_range = (50000, 150000)  # Example ranges for high emergency fund
    medium_economies_range = (20000, 50000)  # Example ranges for medium emergency fund
    low_economies_range = (0, 20000)  # Example ranges for low emergency fund

    # Calculate membership degrees for high, medium, and low emergency fund
    high_economies = triangular_sigmoid(*high_economies_range)
    medium_economies = triangular_sigmoid(*medium_economies_range)
    low_economies = triangular_sigmoid(*low_economies_range)

    membership_high = high_economies(total_economies)
    membership_medium = medium_economies(total_economies)
    membership_low = low_economies(total_economies)

    # Create a dictionary to store the percentages of emergency fund belonging to each income category
    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict


def emergency_fund_membership(income, emergency_fund):
    """
    Determine the membership of an emergency fund value relative to the income in the categories: high, medium, low.
    
    Args:
    - income (float): The income value.
    - emergency_fund (float): The emergency fund value.
    
    Returns:
    - dict: A dictionary showing the percentage of emergency fund belonging to each category.
    """
    
    # Define ranges for emergency fund levels based on a percentage of the income
    # Assume high is 6+ months, medium is 3-6 months, and low is less than 3 months
    high_fund = triangular_sigmoid(0.5 * income, 6 * income)
    medium_fund = triangular_sigmoid(0.25 * income, 3 * income)
    low_fund = triangular_sigmoid(0, 0.25 * income)
    
    # Calculate membership degrees for each emergency fund level
    membership_high = high_fund(emergency_fund)
    membership_medium = medium_fund(emergency_fund)
    membership_low = low_fund(emergency_fund)
    
    # Create a dictionary to store the percentages of the emergency fund belonging to each category
    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }
    
    # Return the dictionary
    return membership_dict

#computes how much progress you have made towards achieving your goal
def goal_membership(total_savings, target_amount):
    """
    Calculate the membership degrees for the goal based on the total savings and target amount.

    Args:
    - total_savings (float): Total savings accumulated for the goal until the present moment.
    - target_amount (float): Target amount for the goal.

    Returns:
    - dict: A dictionary containing the membership degrees for high, medium, and low progress towards the goal.
    """
    # Calculate the progress towards the goal
    progress = total_savings / target_amount

    # Define the ranges for high, medium, and low progress towards the goal
    high_progress_range = (0.8, 1)  # Adjusted for high progress
    medium_progress_range = (0.5, 0.8)  # Adjusted for medium progress
    low_progress_range = (0, 0.5)  # Adjusted for low progress

    # Calculate membership degrees for high, medium, and low progress towards the goal
    high_progress_membership = triangular_sigmoid(*high_progress_range)
    medium_progress_membership = triangular_sigmoid(*medium_progress_range)
    low_progress_membership = triangular_sigmoid(*low_progress_range)

    membership_high = high_progress_membership(progress)
    membership_medium = medium_progress_membership(progress)
    membership_low = low_progress_membership(progress)

    # Create a dictionary to store the percentages of progress towards the goal belonging to each category
    membership_dict = {
        'high': membership_high,
        'medium': membership_medium,
        'low': membership_low
    }

    return membership_dict



from django.shortcuts import render
from .models import Income, TotalExpense
from django.db.models import Sum
from django.utils import timezone

def income_expense_chart(request):
    now = datetime.now()
    month = now.month
    year = now.year

    # Retrieve total income
    income = Income.objects.filter(user=request.user, month=month, year=year).last()
    total_income = income.total_amount

    # Retrieve total expenses
    expenses = TotalExpense.objects.filter(user=request.user, month=month, year=year).last()
    total_expenses = expenses.total_expenses

    return render(request, 'accounts/income_expense_chart.html', {'total_income': total_income, 'total_expenses': total_expenses})


def overview(request):
    user = request.user
    now = datetime.now()
    month = now.month
    year = now.year

    income = Income.objects.filter(user=user, month=month, year=year).first()  # Get the user's income object for the current month and year

    # Filter card incomes for the current month
    card_incomes = CardIncome.objects.filter(income=income, day__month=month, amount__gt=0)

    # Filter cash incomes for the current month
    cash_incomes = CashIncome.objects.filter(income=income, day__month=month, amount__gt=0)

    # Filter expenses for the current month
    expenses = Expense.objects.filter(user=user, day__month=month)

    # Get all goals for the user
    goals = Goal.objects.filter(user=user)

    if month == 1:
        last_month = 12
        year -= 1
    else:
        last_month = month - 1
    economies = Economies.objects.filter(user=user, month=last_month, year=year).last()

    goal_savings = GoalSavings.objects.filter(goal__user=user, month=last_month, year=year).last()

    need = goals.last().target_amount - (goal_savings.total_savings if goal_savings else 0)

    tot_expenses = TotalExpense.objects.filter(user=user, month=month, year=year).last()
    total_expenses = tot_expenses.total_expenses if tot_expenses else 0

    context = {
        'income': income,
        'cash_incomes': cash_incomes,
        'card_incomes': card_incomes,
        'expenses': expenses,
        'goals': goals,
        'economies': economies,
        'goal_savings' : goal_savings,
        'need' : need,
        'total_expenses' : total_expenses
    }
    return render(request, 'accounts/overview.html', context)

