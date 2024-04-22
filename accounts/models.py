from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)   #asa este one to one relationship, un user poate avea doar un income.
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_left = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.IntegerField()
    year = models.IntegerField()

    @classmethod
    def create_or_update_income(cls, user, total_amount, income_left):
        now = timezone.now()
        month = now.month
        year = now.year

        # Check if an income object for the current month and year already exists
        income_obj, created = cls.objects.get_or_create(
            user=user,
            month=month,
            year=year,
            defaults={'total_amount': total_amount, 'income_left': income_left}
        )

        # If the object already existed, update its fields
        if not created:
            income_obj.total_amount = total_amount
            income_obj.income_left = income_left
            income_obj.save()

        return income_obj

class CashIncome(models.Model):
    income = models.ForeignKey(Income, related_name='cash_incomes', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3)
    day = models.DateField(auto_now_add=True)
    hour = models.TimeField(auto_now_add=True)

class CardIncome(models.Model):
    income = models.ForeignKey(Income, related_name='card_incomes', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3)
    day = models.DateField(auto_now_add=True)
    hour = models.TimeField(auto_now_add=True)

#model pt un expense:
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)  # Assuming you want to store the value as a decimal

    #define the choices to store them in the database
    TYPE_CHOICES = (
        ('essential', 'Essential'),
        ('important', 'Important'),
        ('minor', 'Minor'),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    FREQUENCY_CHOICES = (
        ('one_time', 'One Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('6_months', 'Every 6 Months'),
        ('yearly', 'Yearly'),
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='one_time')
    CATEGORY_CHOICES = (
        ('housing', 'Housing'),
        ('food', 'Food'),
        ('health', 'Health'),
        ('utilities', 'Utilities'),
        ('transport', 'Transport'),
        ('personal', 'Personal'),
        ('entertainment', 'Entertainment'),
        ('vices', 'Vices'),
        ('other', 'Other'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    day = models.DateField(auto_now_add=True)
    hour = models.TimeField(auto_now_add=True)
    currency = models.CharField(max_length=3)

#model pt total expenses
class TotalExpense(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_housing_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_food_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_health_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_utilities_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_transport_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_personal_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_entertainment_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_vices_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_other_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.IntegerField()
    year = models.IntegerField()
    

    def update_total_expenses(self):
        self.total_expenses = (
            self.total_housing_expense + 
            self.total_food_expense + 
            self.total_health_expense + 
            self.total_utilities_expense + 
            self.total_transport_expense + 
            self.total_personal_expense + 
            self.total_entertainment_expense + 
            self.total_vices_expense + 
            self.total_other_expense
        )
        self.save()

class Image(models.Model):
    image = models.ImageField(upload_to='images/')    
    #images e folderul din media(care se creeaza automat cand uploadam o imagine) unde se vor pune imaginile uploadate

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class GoalSavings(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    monthly_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @classmethod
    def create_or_update_goal_savings(cls, goal, month, year, monthly_savings=0):
        # Check if a goal savings object for the given goal, month, and year already exists
        goal_savings_obj, created = cls.objects.get_or_create(
            goal=goal,
            month=month,
            year=year,
        )

        # If the object already existed, update its fields
        if not created:
            goal_savings_obj.monthly_savings = monthly_savings
            goal_savings_obj.total_savings += monthly_savings
            goal_savings_obj.save()

        return goal_savings_obj



class Economies(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    monthly_economies = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_economies = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @classmethod
    def create_or_update_economies(cls, user, month, year, monthly_economies=0):
        # Check if an economies object for the given month and year already exists for the user
        economies_obj, created = cls.objects.get_or_create(
            user=user,
            month=month,
            year=year,
        )

        # If the object already existed, update its fields
        if not created:
            # Update the monthly_economies and total_economies fields
            economies_obj.monthly_economies = monthly_economies
            economies_obj.total_economies += monthly_economies
            economies_obj.save()

        return economies_obj

