from .forms import RegisterForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            login(request, user)  # Log in the user
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('/login/')  # Redirect to the home page after successful registration
        else:
            messages.error(request, 'Error in registration. Please correct the form.')

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to a success page, e.g., home page
            #return redirect('home')  # Replace 'home' with the name of your home URL
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')