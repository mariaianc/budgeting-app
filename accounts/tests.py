
from django.test import TestCase
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "budgeting_app.settings")

import django
django.setup()

from django.contrib.auth.models import User

from .forms import RegisterForm
from django.core.exceptions import ValidationError
class RegisterFormTestCase(TestCase):
    def test_valid_form(self):
        # Test a valid form submission
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': 'test1234.',
            'password2': 'test1234.'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        # Test an invalid form submission
        form_data = {
            'username': '',  # Username is required
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': 'test1234',
            'password2': 'test1234'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_password_mismatch(self):
        # Test password mismatch
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': 'test1234',
            'password2': 'differentpassword'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


    def test_clean_username_valid(self):
        # Test cleaning method for a valid username
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': 'test1234.',
            'password2': 'test1234.'
        }
        form = RegisterForm(data=form_data)
        form.is_valid()  # Run validation
        self.assertEqual(form.cleaned_data['username'], 'testuser')

    def test_username_contains_letter(self):
        # Form data with a username that does not contain any letters
        form_data = {
            'username': '1234567890',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': 'test1234.',
            'password2': 'test1234.'
        }
        
        # Instantiate the form with the provided data
        form = RegisterForm(data=form_data)
        
        # Verify that the form is not valid (because the username does not contain any letters)
        self.assertFalse(form.is_valid())
        
        # Verify that the 'username' field has a validation error with the expected message
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'], ['Username must contain at least one letter and can only contain letters and numbers.'])

    def test_unique_username(self):
        # Create a user with the same username as in the form data
        User.objects.create_user(username='testuser')
        
        # Form data with the same username
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': 'test1234.',
            'password2': 'test1234.'
        }
        
        # Instantiate the form with the provided data
        form = RegisterForm(data=form_data)
        
        # Verify that the form is not valid (because of the duplicate username)
        self.assertFalse(form.is_valid())
        
        # Verify that the 'username' field has a validation error with the expected message
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'], ['Username is already taken, choose anotherone.'])

    def test_clean_first_name_invalid(self):
        # Test cleaning method for an invalid first name (does not start with an uppercase letter)
        form_data = {
            'username': 'testuser',
            'first_name': 'john',  # Invalid: does not start with an uppercase letter
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': 'test1234.',
            'password2': 'test1234.'
        }
        form = RegisterForm(data=form_data)
        form.is_valid()  # Run validation
        self.assertIn('first_name', form.errors)
        self.assertEqual(form.errors['first_name'], ['First name must start with an uppercase letter and contain only letters.'])

    def test_clean_last_name_invalid(self):
        # Test cleaning method for an invalid last name (does not start with an uppercase letter)
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'doe',  # Invalid: does not start with an uppercase letter
            'email': 'test@example.com',
            'password1': 'test1234.',
            'password2': 'test1234.'
        }
        form = RegisterForm(data=form_data)
        form.is_valid()  # Run validation
        self.assertIn('last_name', form.errors)
        self.assertEqual(form.errors['last_name'], ['Last name must start with an uppercase letter and contain only letters.'])


    def test_clean_email_unique(self):
        # Create a user with a specific email for testing
        existing_email = 'test@example.com'
        User.objects.create_user(username='existing_user', email=existing_email)

        # Test validation for already existing email
        form_data = {
            'username': 'new_user',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': existing_email,  # Use existing email
            'password1': 'test1234.',
            'password2': 'test1234.'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())  # Form should be invalid
        self.assertIn('email', form.errors)  # Error should be present for email field
        # Compare the error message generated by the form with the expected error message
        self.assertEqual(form.errors['email'], ['Email is used in another account.'])


    def test_clean_password1_valid(self):
        # Test cleaning method for a valid password
        valid_password = 'Password123!'
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': valid_password,
            'password2': valid_password
        }
        form = RegisterForm(data=form_data)
        form.is_valid()  # Run validation
        self.assertEqual(form.cleaned_data['password1'], valid_password)

    

    def test_clean_password1_too_short(self):
        password = 'we1.'
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': password,
            'password2': password
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())  # Form should be invalid
        self.assertIn('password1', form.errors)  # Error should be present for password1 field
        self.assertEqual(form.errors['password1'], ['Password must be at least 8 characters long.'])


    def test_clean_password1_no_letter(self):
        password = '12345673.'
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': password,
            'password2': password
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())  # Form should be invalid
        self.assertIn('password1', form.errors)  # Error should be present for password1 field
        # Check if the correct error message is generated
        self.assertEqual(form.errors['password1'], ['Password must contain at least one letter.'])


    def test_clean_password1_no_special_char(self):
        # Test cleaning method for a password that contains no special characters
        password = 'Password3'
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': password,
            'password2': password
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())  # Form should be invalid
        self.assertIn('password1', form.errors)  # Error should be present for password1 field
        # Check if the correct error message is generated
        self.assertEqual(form.errors['password1'], ['Password must contain at least one special character.'])


    def test_clean_password1_no_digit(self):
        # Test cleaning method for a password that does not contain any digits
        password = 'Password!'
        form_data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'password1': password,
            'password2': password
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())  # Form should be invalid
        self.assertIn('password1', form.errors)  # Error should be present for password1 field
        # Check if the correct error message is generated
        self.assertEqual(form.errors['password1'], ['Password must contain at least one digit.'])


from .forms import LoginForm
class LoginFormTestCase(TestCase):
    def setUp(self):
        # Create a user for testing authentication
        self.user = User.objects.create_user(username='testuser', password='test1234')

    def test_valid_form(self):
        # Test a valid form submission
        form_data = {
            'username': 'testuser',
            'password': 'test1234'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        # Test an invalid form submission
        form_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_username_not_found(self):
        # Test that an error is raised when the username does not exist
        form_data = {
            'username': 'nonexistentuser',
            'password': 'test1234'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_incorrect_password(self):
        # Test that an error is raised when the password is incorrect
        form_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_empty_username(self):
        # Test that an error is raised when the username field is empty
        form_data = {
            'username': '',
            'password': 'test1234'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_empty_password(self):
        # Test that an error is raised when the password field is empty
        form_data = {
            'username': 'testuser',
            'password': ''
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)



from .forms import IncomeForm
from decimal import Decimal, ROUND_DOWN
class IncomeFormTestCase(TestCase):
    def test_valid_form(self):
        # Test a valid form submission
        form_data = {
            'cash_amount': '100.00',
            'card_amount': '50.50'
        }
        form = IncomeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        # Test an invalid form submission
        form_data = {
            'cash_amount': 'invalid',  # Invalid cash amount
            'card_amount': '50.50'
        }
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_clean_cash_amount(self):
        # Test cleaning method for cash amount
        form_data = {
            'cash_amount': '100.00',  #nu inteleg de ce nu merge cu 3 zecimale
            'card_amount': ''
        }
        form = IncomeForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)  # Print form errors if validation fails
        cleaned_cash_amount = form.clean_cash_amount()  # Explicitly call the clean_cash_amount method
        self.assertEqual(cleaned_cash_amount, Decimal('100.00'))

    def test_clean_card_amount(self):
        # Test cleaning method for card amount
        form_data = {
            'cash_amount': '',
            'card_amount': '50.50'  # Test with more than 2 decimal places
        }
        form = IncomeForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)  # Print form errors if validation fails
        self.assertEqual(form.cleaned_data['card_amount'], Decimal('50.50'))


    def test_optional_fields(self):
        # Test that both fields can be empty
        form_data = {
            'cash_amount': '',
            'card_amount': ''
        }
        form = IncomeForm(data=form_data)
        self.assertTrue(form.is_valid())


from .forms import ExpenseInputForm
class ExpenseInputFormTestCase(TestCase):
    def test_valid_form(self):
        # Test a valid form submission
        form_data = {
            'type': 'essential',
            'frequency': 'daily',
            'category': 'housing',
            'value': '100.00'
        }
        form = ExpenseInputForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        # Test an invalid form submission
        form_data = {
            'type': '',  # Type is required
            'frequency': 'daily',
            'category': 'housing',
            'value': '100.00'
        }
        form = ExpenseInputForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_type_choices(self):
        # Test type choices
        form = ExpenseInputForm()
        type_choices = dict(form.fields['type'].choices)
        self.assertEqual(type_choices, {
            'essential': 'Essential',
            'important': 'Important',
            'minor': 'Minor'
        })

    def test_frequency_choices(self):
        # Test frequency choices
        form = ExpenseInputForm()
        frequency_choices = dict(form.fields['frequency'].choices)
        self.assertEqual(frequency_choices, {
            'one_time': 'One Time',
            'daily': 'Daily',
            'weekly': 'Weekly',
            'monthly': 'Monthly',
            '6_months': 'Every 6 Months',
            'yearly': 'Yearly'
        })

    def test_category_choices(self):
        # Test category choices
        form = ExpenseInputForm()
        category_choices = dict(form.fields['category'].choices)
        self.assertEqual(category_choices, {
            'housing': 'Housing',
            'food': 'Food',
            'health': 'Health',
            'utilities': 'Utilities',
            'transport': 'Transport',
            'personal': 'Personal',
            'entertainment': 'Entertainment',
            'vices': 'Vices',
            'other': 'Other'
        })

    def test_required_value_field(self):
        # Test required value field
        form_data = {
            'type': 'essential',
            'frequency': 'daily',
            'category': 'housing',
            'value': ''
        }
        form = ExpenseInputForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('value', form.errors)


from django.test import TestCase
from .forms import ImageForm

from django.core.files.uploadedfile import SimpleUploadedFile
class ImageFormTestCase(TestCase):
    
    def test_valid_form(self):
        # Simulate a valid image upload
        image_path = 'C:\\Users\\Maria\\Downloads\\receipt.jpg'
        with open(image_path, 'rb') as image_file:
            form_data = {
                'image': SimpleUploadedFile(image_file.name, image_file.read())  # Create a SimpleUploadedFile object
            }
            form = ImageForm(data={}, files=form_data)
            self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_form(self):
        # Test an invalid form submission (empty image field)
        form_data = {
            'image': ''
        }
        form = ImageForm(data=form_data)
        self.assertFalse(form.is_valid())


from .forms import GoalForm, SplitIncomeForm
class GoalFormTestCase(TestCase):
    def test_valid_goal_form(self):
        # Test a valid goal form submission
        form_data = {
            'title': 'Save for vacation',
            'target_amount': '1000.00'
        }
        form = GoalForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_goal_form(self):
        # Test an invalid goal form submission
        form_data = {
            'title': '',  # Title is required
            'target_amount': '-100.00'  # Target amount should be positive
        }
        form = GoalForm(data=form_data)
        self.assertFalse(form.is_valid())

class SplitIncomeFormTestCase(TestCase):
    def test_valid_split_income_form(self):
        # Test a valid split income form submission
        form_data = {
            'economies_amount': '500.00',
            'goal_amount': '300.00'
        }
        form = SplitIncomeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_split_income_form(self):
        # Test an invalid split income form submission
        form_data = {
            'economies_amount': '-100.00',  # Amounts should be positive
            'goal_amount': '500.00'
        }
        form = SplitIncomeForm(data=form_data)
        self.assertFalse(form.is_valid())



from django.utils import timezone
from .models import Income
class IncomeModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')
    
    def test_create_or_update_income_create(self):
        # Test creating a new income object
        total_amount = 1000
        income_left = 500
        income_obj = Income.create_or_update_income(self.user, total_amount, income_left)

        # Check if the income object is created
        self.assertIsNotNone(income_obj)
        self.assertEqual(income_obj.total_amount, total_amount)
        self.assertEqual(income_obj.income_left, income_left)

    def test_create_or_update_income_update(self):
        # Test updating an existing income object
        total_amount = 1500
        income_left = 800

        # Create an income object for the current month and year
        now = timezone.now()
        month = now.month
        year = now.year
        income_obj = Income.objects.create(
            user=self.user,
            total_amount=1000,
            income_left=500,
            month=month,
            year=year
        )

        # Call create_or_update_income with updated values
        updated_income_obj = Income.create_or_update_income(self.user, total_amount, income_left)

        # Check if the income object is updated
        self.assertEqual(updated_income_obj.pk, income_obj.pk)
        self.assertEqual(updated_income_obj.total_amount, total_amount)
        self.assertEqual(updated_income_obj.income_left, income_left)


from .models import TotalExpense

class TotalExpenseModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
    
    def test_update_total_expenses(self):
        # Create a TotalExpense object
        total_expense = TotalExpense.objects.create(
            user=self.user,
            total_housing_expense=100,
            total_food_expense=200,
            total_health_expense=50,
            total_utilities_expense=80,
            total_transport_expense=70,
            total_personal_expense=120,
            total_entertainment_expense=90,
            total_vices_expense=30,
            total_other_expense=60,
            total_expenses=0,  # Initially set to 0
            month=5,
            year=2024
        )

        # Call the update_total_expenses method
        total_expense.update_total_expenses()

        # Retrieve the updated total_expense object from the database
        updated_total_expense = TotalExpense.objects.get(pk=total_expense.pk)

        # Check if the total_expenses field is updated correctly
        expected_total_expenses = (
            total_expense.total_housing_expense + 
            total_expense.total_food_expense + 
            total_expense.total_health_expense + 
            total_expense.total_utilities_expense + 
            total_expense.total_transport_expense + 
            total_expense.total_personal_expense + 
            total_expense.total_entertainment_expense + 
            total_expense.total_vices_expense + 
            total_expense.total_other_expense
        )
        self.assertEqual(updated_total_expense.total_expenses, expected_total_expenses)



from accounts.models import Goal, GoalSavings
class GoalSavingsModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.goal = Goal.objects.create(user=self.user, title='Test Goal', target_amount=1000, achieved=False)

    def test_create_or_update_goal_savings(self):
        month = 5
        year = 2024
        monthly_savings = 200

        # Create or update goal savings for the first time
        goal_savings_obj = GoalSavings.create_or_update_goal_savings(
            goal=self.goal,
            month=month,
            year=year,
            monthly_savings=monthly_savings
        )

        # Check if the object is created correctly
        self.assertIsNotNone(goal_savings_obj)
        self.assertEqual(goal_savings_obj.goal, self.goal)
        self.assertEqual(goal_savings_obj.month, month)
        self.assertEqual(goal_savings_obj.year, year)
        self.assertEqual(goal_savings_obj.monthly_savings, monthly_savings)
        self.assertEqual(goal_savings_obj.total_savings, monthly_savings)

        # Update the goal savings object with new monthly savings
        new_monthly_savings = 300
        updated_goal_savings_obj = GoalSavings.create_or_update_goal_savings(
            goal=self.goal,
            month=month,
            year=year,
            monthly_savings=new_monthly_savings
        )

        # Check if the object is updated correctly
        self.assertEqual(updated_goal_savings_obj.monthly_savings, new_monthly_savings)
        self.assertEqual(updated_goal_savings_obj.total_savings, monthly_savings + new_monthly_savings)



from accounts.models import Economies

class EconomiesModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_create_or_update_economies(self):
        month = 5
        year = 2024
        monthly_economies = 200

        # Create or update economies for the first time
        economies_obj = Economies.create_or_update_economies(
            user=self.user,
            month=month,
            year=year,
            monthly_economies=monthly_economies
        )

        # Check if the object is created correctly
        self.assertIsNotNone(economies_obj)
        self.assertEqual(economies_obj.user, self.user)
        self.assertEqual(economies_obj.month, month)
        self.assertEqual(economies_obj.year, year)
        self.assertEqual(economies_obj.monthly_economies, monthly_economies)
        self.assertEqual(economies_obj.total_economies, monthly_economies)

        # Update the economies object with new monthly economies
        new_monthly_economies = 300
        updated_economies_obj = Economies.create_or_update_economies(
            user=self.user,
            month=month,
            year=year,
            monthly_economies=new_monthly_economies
        )

        # Check if the object is updated correctly
        self.assertEqual(updated_economies_obj.monthly_economies, new_monthly_economies)
        self.assertEqual(updated_economies_obj.total_economies, monthly_economies + new_monthly_economies)



from django.test import TestCase, Client
from django.urls import reverse
from accounts.forms import RegisterForm
class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_post(self):
        # Create a POST request with form data
        post_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword1!',
            'password2': 'testpassword1!',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        response = self.client.post(reverse('register'), data=post_data)
        
        # Check if the user is created and redirected
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue(User.objects.filter(username='testuser').exists())  # User created


    def test_register_invalid_form(self):
        # Create a POST request with invalid form data
        post_data = {
            'username': '',  # Invalid username
            'first_name': '',  # Invalid first name
            'last_name': '',  # Invalid last name
            'email': 'invalid-email',  # Invalid email format
            'password1': 'password',  # Password too short
            'password2': 'password',  # Passwords don't match
        }
        response = self.client.post(reverse('register'), data=post_data)
        
        # Check if the response status code is 200 (form is re-rendered)
        self.assertEqual(response.status_code, 200)


    def test_register_view_get(self):
        # Create a test client
        client = Client()
        
        # Make a GET request to the register view
        response = client.get(reverse('register'))  # Assuming you have a URL name for the register view
        
        # Check that the response is a success (status code 200)
        self.assertEqual(response.status_code, 200)
        
        # Check that the response has content
        self.assertTrue(response.content)

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.forms import LoginForm

class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_login_post_valid_credentials(self):
        # Create a POST request with valid credentials
        post_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), data=post_data)
        
        # Check if the user is redirected after successful login
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertIn('_auth_user_id', self.client.session)  # User is logged in

    def test_login_post_invalid_credentials(self):
        # Create a POST request with invalid credentials
        post_data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('login'), data=post_data)
        
        # Check if the user is not redirected after unsuccessful login
        self.assertEqual(response.status_code, 200)  # Status code 200 means the form is re-rendered
        self.assertNotIn('_auth_user_id', self.client.session)  # User is not logged in

    def test_login_view_get(self):
        # Make a GET request to the login view
        response = self.client.get(reverse('login')) 
        
        # Check that the response is a success (status code 200)
        self.assertEqual(response.status_code, 200)
        
        # Check that the response has content
        self.assertTrue(response.content)


    def test_login_invalid_form(self):
        # Create a POST request with invalid form data
        post_data = {
            'username': '',  # Invalid username
            'password': '',  # Invalid password
        }
        response = self.client.post(reverse('login'), data=post_data)
        
        # Check if the response status code is 200 (form is re-rendered)
        self.assertEqual(response.status_code, 200)


class HomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        # Make a GET request to the home view
        response = self.client.get(reverse('home'))
        
        # Check that the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct template is used
        # self.assertTemplateUsed(response, 'accounts/home.html')
    

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Income, CashIncome, CardIncome
from .forms import IncomeForm

class IncomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_income_view_get(self):
        # Make a GET request to the income view
        response = self.client.get(reverse('income'))
        
        # Check that the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct template is used
        #self.assertTemplateUsed(response, 'accounts/income.html')

        # Additional tests for initialization of variables can be added here

    def test_income_view_post(self):
        # Make a POST request to the income view with valid data
        post_data = {
            'cash_amount': 100,
            'card_amount': 200,
            'action': 'compute',
        }
        response = self.client.post(reverse('income'), data=post_data)
        
        # Check that the response redirects (status code 302)
        self.assertEqual(response.status_code, 302)

        # Additional tests for computation logic can be added here

    def test_income_view_undo(self):
        # Make a POST request to the income view to compute data
        post_data = {
            'cash_amount': 100,
            'card_amount': 200,
            'action': 'compute',
        }
        self.client.post(reverse('income'), data=post_data)

        # Make a POST request to the income view to undo computation
        post_data_undo = {'action': 'undo'}
        response_undo = self.client.post(reverse('income'), data=post_data_undo)

        # Check that the response redirects (status code 302)
        self.assertEqual(response_undo.status_code, 302)

        # Additional tests for undo logic can be added here

    # Additional tests for edge cases and error handling can be added here


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Expense, TotalExpense
from .forms import ExpenseInputForm

class CreateExpenseViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_create_expense_view_get(self):
        # Make a GET request to the create_expense view
        response = self.client.get(reverse('create_expense'))
        
        # Check that the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct template is used
        #self.assertTemplateUsed(response, 'accounts/expense.html')


    def test_create_expense_view_post(self):
        # Make a POST request to the create_expense view with valid data
        post_data = {
            'value': 100,  # Example expense value
            # Add other required fields for the form here
        }
        response = self.client.post(reverse('create_expense'), data=post_data)
        
        # Check that the response redirects (status code 302)
        self.assertEqual(response.status_code, 200)

    def test_get_expense_form(self):
        # Make a GET request to the create_expense view
        response = self.client.get(reverse('create_expense'))
        
        # Check that the response is successful and the form is rendered
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'accounts/expense.html')
        # self.assertTrue('form' in response.context)

    def test_create_expense_with_valid_form(self):
        # Log in as the user
        self.client.login(username='test_user', password='test_password')
        self.income = Income.objects.create(user=self.user, month=5,year=2024, income_left=1000.00)  # Adjust the month and income_left as needed

        # Prepare form data
        form_data = {
            'value': '10.00',  # Assuming value is a DecimalField
            'type': 'important',
            'frequency': 'one_time',
            'category': 'food',
        }

        # Make a POST request to the view
        response = self.client.post(reverse('create_expense'), form_data)

        # Check if the expense was created
        #self.assertEqual(Expense.objects.count(), 1)

        # Check if the user associated with the expense is correct
        expense = Expense.objects.last()
        self.assertEqual(expense.user, self.user)

        # Check if the income left was updated
        income = Income.objects.get(user=self.user, month=expense.day.month)
        self.assertEqual(income.income_left, 990.00)

        # Check if the total expenses were updated
        total_expense = TotalExpense.objects.get(user=self.user, month=expense.day.month, year=expense.day.year)
        # Assert your expectations about the total expenses fields here

        # Check if the response is a redirect
        self.assertRedirects(response, reverse('create_expense'))  # Assuming the view redirects to itself



from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from .views import upload_image
from .models import Image

class UploadImageViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='test_user', password='test_password')

        # Create a test image
        self.image = Image.objects.create(image='test_image.jpg')

    def test_upload_image_success(self):
        # Log in as the test user
        self.client.login(username='test_user', password='test_password')

        # Prepare image file data
        image_path = 'C:\\Users\\Maria\\Downloads\\receipt.jpg'
        with open(image_path, 'rb') as img_file:
            image_data = {'image': img_file}

            # Make a POST request with valid image data
            response = self.client.post(reverse('upload_image'), image_data, format='multipart')

            # Check if the response is successful
            self.assertEqual(response.status_code, 200)


    def test_render_upload_image_form(self):
        # Log in as the test user
        self.client.login(username='test_user', password='test_password')

        # Make a GET request to the upload_image view
        response = self.client.get(reverse('upload_image'))

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)


from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from .views import create_goal
from .models import Goal
from .forms import GoalForm

class CreateGoalViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='test_user', password='test_password')

    def test_create_goal_no_existing_goals(self):
        # Log in as the test user
        self.client.login(username='test_user', password='test_password')

        # Make a POST request to create a goal when no existing goals exist
        response = self.client.post(reverse('create_goal'))

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

  
    def test_create_goal_with_unachieved_goals(self):
        # Log in as the test user
        self.client.login(username='test_user', password='test_password')

        # Create an existing unachieved goal for the user
        existing_goal = Goal.objects.create(user=self.user, title='Test Goal', target_amount=100.00, achieved=False)

        # Make a POST request to create a new goal
        response = self.client.post(reverse('create_goal'))
        print(response.content.decode())
        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

    
    def test_create_goal_save_to_database(self):
        # Log in as the test user
        self.client.login(username='test_user', password='test_password')

        # Prepare form data
        form_data = {
            'title': 'Test Goal',
            'target_amount': 100.00,
        }

        # Make a POST request to create a new goal
        response = self.client.post(reverse('create_goal'), form_data)

        # Check if the goal was saved to the database
        #self.assertEqual(Goal.objects.count(), 1)

        # Retrieve the created goal object from the database
        created_goal = Goal.objects.last()

        # Check if the created goal has the correct attributes
        self.assertEqual(created_goal.title, form_data['title'])
        self.assertEqual(created_goal.target_amount, form_data['target_amount'])

        # Check if the created goal is associated with the correct user
        self.assertEqual(created_goal.user, self.user)


    def test_create_goal_with_get_request(self):
        # Log in as the test user
        self.client.login(username='test_user', password='test_password')

        # Make a GET request to the create_goal view
        response = self.client.get(reverse('create_goal'))

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from .views import chat_view

class ChatViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='test_user', password='test_password')
        
        # Create a request factory
        self.factory = RequestFactory()

    def test_chat_view_with_valid_post_request(self):
        # Create a mock OpenAI client
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = "Assistant response"

        # Set up the request
        request = self.factory.post('/chat_view/', {'message': 'User message'})
        request.user = self.user
        
        # Set up the environment variable
        with patch('accounts.views.OpenAI', return_value=mock_client):
            # Call the chat_view function
            response = chat_view(request)

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)




