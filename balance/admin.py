from django.contrib import admin
from .models import Balance

class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_expenses', 'total_incomes', 'balance')
    readonly_fields = ('total_expenses', 'total_incomes', 'balance')

admin.site.register(Balance, BalanceAdmin)
