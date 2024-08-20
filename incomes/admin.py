from django.contrib import admin
from .models import Income, Category, Account
# Register your models here.

class IncomeAdmin(admin.ModelAdmin):
    list_display = ('formatted_date', 'owner', 'description', 'category', 'account', 'amount')
    search_fields = ('owner__username', 'description', 'category', 'account', 'amount')
    list_per_page = 20
    
    def formatted_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')
    formatted_date.admin_order_field = 'date'  # Allows sorting by this field in the admin
    formatted_date.short_description = 'Date'  # Column header in the admin

admin.site.register(Income, IncomeAdmin)
#admin.site.register(Category)
#admin.site.register(Account)