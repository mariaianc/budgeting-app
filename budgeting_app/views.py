from django.http import JsonResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist


#create views that handle the URLs related to your budgeting app. 
# The reason you have these view functions is to render the corresponding
# HTML templates when the user accesses the URLs associated with them. 
# This allows Django to dynamically generate HTML content based on the views and templates you've defined.
    
def register(request):
    try:
        return render(request, 'accounts/register.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')
    
def login(request):
    try:
        return render(request, 'accounts/login.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')
    
def home(request):
    try:
        return render(request, 'accounts/home.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')

def income(request):
    try:
        return render(request, 'accounts/income.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')
    
def income_details(request):
    try:
        return render(request, 'accounts/income_details.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')

def create_expense(request):
    try:
        return render(request, 'accounts/expense.html')
    except TemplateDoesNotExist:
        return render(request, 'main_index_not_fount.html')

def upload_image(request):
    try:
        return render(request, 'accounts/upload_image.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')

def create_goal(request):
    try:
        return render(request, 'accounts/goal.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')
    
def all_goals(request):
    try:
        return render(request, 'accounts/all_goals.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')
    

def test_openai_api_key(request):
    try:
        return render(request, 'accounts/openai_result.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')
    

def chat_view(request):
    try:
        return render(request, 'accounts/chat.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')
    

def split_income(request):
    try:
        return render(request, 'accounts/split_income.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')