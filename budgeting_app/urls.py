"""
URL configuration for budgeting_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import *   # register, login, home, income, income_details, create_expense, upload_image, create_goal, all_goals, test_openai_api_key, chat_view
from django.conf import settings
from django.conf.urls.static import static

# superuser: username: root; password: password

urlpatterns = [
   #path('', register, name="register"),
   path('admin/', admin.site.urls),
   path('register/', register, name = "register"),
   path('', login, name = "login"),
   path('login/', login, name="login"),
   path('home/', home, name = "home"),
   path('income/', income, name = "income"),
   path('income_details/', income_details, name = "income_details"),
   path('create_expense/', create_expense, name='create_expense'),
   path('upload_image/', upload_image, name='upload_image'),
   path('create_goal/', create_goal, name='create_goal'),
   path('see_goals/', all_goals, name='all_goals'),
   #path('test_openai_api/', test_openai_api_key, name='test_openai_api_key'),
   path('chat/', chat_view, name='chat_view'),
   path('split_income/', split_income, name='split_income'),

   
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT) #pt upload images, automatically creates an url for the database.
