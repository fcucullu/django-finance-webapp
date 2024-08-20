from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Balance

@login_required
def balance_view(request):
    balance, created = Balance.objects.get_or_create(user=request.user)
    balance = Balance.objects.get(user=request.user)
    balance.update_balance()
    return render(request, 'balance/dashboard.html', {'balance': balance})
