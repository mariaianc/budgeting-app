from django.http import JsonResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist


#create views that handle the URLs related to your budgeting app. 
    
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
