from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .models import Expense, Category, Account
from django.contrib import messages
from decimal import Decimal

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    categories = Category.objects.all()
    accounts = Account.objects.all()
    #expenses = Expense.objects.filter(owner=request.user) If I want to filter expenses only by owner (case of a public app)
    expenses = Expense.objects.all()
    context = {
        'categories': categories,
        'accounts': accounts,
        'expenses': expenses
    }
    return render(request, 'expenses/index.html', context)



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
        date = request.POST.get('date', '')
        description = request.POST.get('description', '')
        amount = request.POST.get('amount', '').replace(',','.')
        amount_decimal = Decimal(amount).quantize(Decimal('0.01'))
        category = request.POST.get('category', '')
        account = request.POST.get('account', '')

        is_invalid_input = not all([date, description, amount, category, account])
        is_invalid_category = category == "--- Select Category ---"
        is_invalid_account = account == "--- Select Account ---"
        conditions = is_invalid_input or is_invalid_category or is_invalid_account

        if conditions:
            messages.error(request, 'All fields are mandatory')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(
            owner=request.user,
            date=date,
            description=description,
            amount=amount_decimal,
            category=category,
            account=account
        )

        messages.success(request, 'Expense added successfully')
        return redirect('expenses')
