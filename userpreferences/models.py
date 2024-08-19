from django.db import models
from django.contrib.auth.models import User

# Default values as callables
def get_default_categories_expenses():
    return ['Bills & Services', 'Clothes', 'Dog', 'Food Out', 'Fun', 'Gifts', 'Health & Body & Mind', 'Home', 'Income', 'Rent', 'Supermarket', 'Transfers', 'Travel']

def get_default_categories_incomes():
    return ['Salary', 'Sales']

def get_default_accounts():
    return ['Bank', 'Cash']


class UserPreferences(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    currency = models.CharField(default="EUR - Euro", max_length=255)
    currency_code = models.CharField(default="EUR", max_length=10)
    rows_per_page = models.IntegerField(default=25)
    categories_incomes = models.JSONField(default=get_default_categories_incomes)
    categories_expenses = models.JSONField(default=get_default_categories_expenses)
    accounts = models.JSONField(default=get_default_accounts)

    def __str__(self):
        return f"{self.user.username}'s preferences"
