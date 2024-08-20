from django.db import models
from django.contrib.auth.models import User
from expenses.models import Expense
from incomes.models import Income 
from configuration.settings import FILTER_BY_OWNER

class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_incomes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def update_balance(self):
        self.total_expenses = Expense.objects.filter(owner=request.user).aggregate(total=models.Sum('amount'))['total'] or 0 if FILTER_BY_OWNER else Expense.objects.all().aggregate(total=models.Sum('amount'))['total'] or 0
        self.total_incomes = Income.objects.filter(owner=request.user).aggregate(total=models.Sum('amount'))['total'] or 0 if FILTER_BY_OWNER else Income.objects.all().aggregate(total=models.Sum('amount'))['total'] or 0
        self.balance = self.total_incomes - self.total_expenses
        self.save()

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"
