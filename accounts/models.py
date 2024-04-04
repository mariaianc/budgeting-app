from django.db import models
from django.contrib.auth.models import User

class Income(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)   #asa este one to one relationship, un user poate avea doar un income.
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3)

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
