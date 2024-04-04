from django.contrib import admin
from .models import Income, CashIncome, CardIncome

class IncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'currency')  # Include 'id' and 'user' (foreign key) in the list display

class CashIncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'income', 'amount', 'currency', 'day', 'hour')  # Include 'id', 'income' (foreign key), and other fields

class CardIncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'income', 'amount', 'currency', 'day', 'hour')  # Include 'id', 'income' (foreign key), and other fields

admin.site.register(Income, IncomeAdmin)
admin.site.register(CashIncome, CashIncomeAdmin)
admin.site.register(CardIncome, CardIncomeAdmin)
