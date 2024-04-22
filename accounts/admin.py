from django.contrib import admin
from .models import Income, CashIncome, CardIncome

class IncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'income_left', 'month', 'year')

class CashIncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'income', 'amount', 'currency', 'day', 'hour')

class CardIncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'income', 'amount', 'currency', 'day', 'hour')

admin.site.register(Income, IncomeAdmin)
admin.site.register(CashIncome, CashIncomeAdmin)
admin.site.register(CardIncome, CardIncomeAdmin)

from .models import Expense, TotalExpense

# class ExpenseAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'value', 'type', 'frequency', 'category', 'day', 'hour', 'currency')

# class TotalExpenseAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'total_housing_expense', 'total_food_expense', 'total_health_expense', 
#                     'total_utilities_expense', 'total_transport_expense', 'total_personal_expense', 
#                     'total_entertainment_expense', 'total_vices_expense', 'total_other_expense', 
#                     'total_expenses')


admin.site.register(Expense)
admin.site.register(TotalExpense)
