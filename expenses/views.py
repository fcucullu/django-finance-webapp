from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .models import Expense, Category, Account
from userpreferences.models import UserPreferences
from django.contrib import messages
from decimal import Decimal
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db.models import Q
from balance.models import Balance
from django.db.models import Sum
import datetime
from configuration.settings import DEFAULT_DAYS_IN_TIME_INTERVALS

#########################################################
##                 START VIEWS SECTION                 ##
#########################################################

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    categories = user_preferences.categories_expenses
    accounts = user_preferences.accounts
    search_text = request.GET.get('search', '')  # Capture searchText from query parameters

    # Determine the base queryset depending on ownership filter
    expenses = Expense.objects.filter(owner=request.user)

    # Apply filtering if searchText is present
    if search_text:
        expenses = expenses.filter(
            Q(amount__icontains=search_text) |
            Q(date__icontains=search_text) |
            Q(description__icontains=search_text) |
            Q(category__icontains=search_text) |
            Q(account__icontains=search_text)
        )

    expenses = expenses.order_by('-date')
    
    paginator = Paginator(expenses, user_preferences.rows_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'accounts': accounts,
        'expenses': expenses,
        'user_preferences': user_preferences,
        'page_obj': page_obj,
        'search_text': search_text
    }
    return render(request, 'expenses/expenses.html', context)

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_expense(request):
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    categories = user_preferences.categories_expenses
    accounts = user_preferences.accounts
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
        try:
            amount_decimal = Decimal(amount).quantize(Decimal('0.01'))
        except:
            messages.error(request, 'Amount is invalid')
            return render(request, 'expenses/add_expense.html', context)

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

        balance, created = Balance.objects.get_or_create(user=request.user)
        balance.update_balance(request)

        messages.success(request, 'Expense added successfully')
        return redirect('expenses')
    

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_expense(request, id):
    expense=Expense.objects.get(pk=id)
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    categories = user_preferences.categories_expenses
    accounts = user_preferences.accounts
    context = {
        'expense': expense,
        'categories': categories,
        'accounts': accounts,
        'values': expense,
    }
    
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)
    
    if request.method == 'POST':
        date = request.POST.get('date', '')
        description = request.POST.get('description', '')
        amount = request.POST.get('amount', '').replace(',','.')
        try:
            amount_decimal = Decimal(amount).quantize(Decimal('0.01'))
        except:
            messages.error(request, 'Amount is invalid')
            return render(request, 'expenses/edit_expense.html', context)

        category = request.POST.get('category', '')
        account = request.POST.get('account', '')

        is_invalid_input = not all([date, description, amount, category, account])
        is_invalid_category = category == "--- Select Category ---"
        is_invalid_account = account == "--- Select Account ---"
        conditions = is_invalid_input or is_invalid_category or is_invalid_account

        if conditions:
            messages.error(request, 'All fields are mandatory')
            return render(request, 'expenses/edit_expense.html', context)

        expense.owner=request.user
        expense.date=date
        expense.description=description
        expense.amount=amount_decimal
        expense.category=category
        expense.account=account
        expense.save()

        balance, created = Balance.objects.get_or_create(user=request.user)
        balance.update_balance(request)

        messages.success(request, 'Expense updated successfully')
        return redirect('expenses')
    

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def expenses_summary(request):
    intervals = list(DEFAULT_DAYS_IN_TIME_INTERVALS.keys())
    return render(request, 'expenses/expenses_summary.html', {"intervals": intervals})


#########################################################
##               START ENDPOINT SECTION                ##
#########################################################

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()

    balance, created = Balance.objects.get_or_create(user=request.user)
    balance.update_balance(request)

    messages.success(request, 'Expense deleted successfully')
    return redirect('expenses')


@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_expenses_by_category(request, interval, calculation_type="total"):
    today = datetime.date.today()
    delta_days = DEFAULT_DAYS_IN_TIME_INTERVALS[interval]
    start_date = today - datetime.timedelta(days=delta_days)

    expenses = Expense.objects.filter(owner=request.user, date__gte=start_date, date__lte=today)

    result = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def calculate_total(category):
        return expenses.filter(category=category).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    def calculate_mean(category):
        return expenses.filter(category=category).aggregate(mean_amount=Avg('amount'))['mean_amount'] or 0

    def calculate_proportion(category):
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 1
        category_total = calculate_total(category)
        return (category_total / total_expense) * 100 if total_expense > 0 else 0

    calculation_function_map = {
        "total": calculate_total,
        "mean": calculate_mean,
        "proportions": calculate_proportion,
    }

    calculation_function = calculation_function_map.get(calculation_type, calculate_total)

    for c in category_list:
        result[c] = calculation_function(c)

    return JsonResponse({'expenses_by_category': result}, safe=False)

