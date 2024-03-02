from django.http import JsonResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist

    
def signup(request):
    try:
        return render(request, 'accounts/register.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')
    
def login(request):
    try:
        return render(request, 'accounts/login.html')
    except TemplateDoesNotExist :
        return render(request, 'main_index_not_fount.html')