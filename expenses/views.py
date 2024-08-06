from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .models import Expense, Category, Account
from django.contrib import messages

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    categories = Category.objects.all()
    account = Account.objects.all()
    return render(request, 'expenses/index.html')

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_expense(request):
    categories = Category.objects.all()
    accounts = Account.objects.all()
    context = {
        'categories': categories,
        'accounts': accounts,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        description = request.POST.get('description', '')
        amount = request.POST.get('amount')
        category = request.POST.get('category', '')
        account = request.POST.get('account', '')

        conditions = not all([description, 
                              amount, 
                              category != "--- Select Account ---", 
                              account != "--- Select Account ---"])

        if conditions:
            messages.error(request, 'All fields are mandatory')
            return render(request, 'expenses/add_expense.html', context)
