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
import pandas as pd
from collections import defaultdict
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

import traceback

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_expenses_by_category(request, interval):
    # Get the calculation_type from query parameters
    calculation_type = request.GET.get('calculation_type')

    print(f"\n### Received Calculation Type: {calculation_type} ###")

    try:
        today = datetime.date.today()
        delta_days = DEFAULT_DAYS_IN_TIME_INTERVALS.get(interval, [365])[0]
        start_date = today - datetime.timedelta(days=delta_days)

        expenses = Expense.objects.filter(owner=request.user, date__gte=start_date, date__lte=today)

        result = {}

        def get_category(expense):
            return expense.category

        category_list = list(set(map(get_category, expenses)))

        def calculate_total(request, start_date, today, interval):
            print("\nCalculating Total...\n")
            total_result = build_datasets_for_total_chart(request, start_date, today, interval)
            print(f"\n### Total Calculation Result: {total_result} ###\n")
            return total_result

        def calculate_mean(category):
            mean_result = expenses.filter(category=category).aggregate(mean_amount=Avg('amount'))['mean_amount'] or 0
            print(f"\n### Mean for {category}: {mean_result} ###\n")
            return mean_result

        def calculate_proportion(category):
            total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 1
            category_total = expenses.filter(category=category).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
            proportion_result = (category_total / total_expense) * 100 if total_expense > 0 else 0
            print(f"\n### Proportion for {category}: {proportion_result}% ###\n")
            return proportion_result

        calculation_function_map = {
            "total": lambda: calculate_total(request, start_date, today, interval),
            "mean": lambda category: calculate_mean(category),
            "proportions": lambda category: calculate_proportion(category),
        }

        calculation_function = calculation_function_map.get(calculation_type, lambda: None)

        if calculation_type == "total":
            result = calculation_function()
        elif calculation_type in ["mean", "proportions"]:
            print(f"\n### Categories to Process: {category_list} ###\n")
            result = {
                'labels': category_list,
                'datasets': [{
                    'label': calculation_type.capitalize(),
                    'data': [calculation_function(category) for category in category_list],
                    'borderWidth': 1,
                }]
            }
        else:
            result = {"error": "Invalid calculation type."}

        print(f"\n### Final Result for {calculation_type}: {result} ###\n")

        return JsonResponse({'expenses_by_category': result}, safe=False)

    except Exception as e:
        print(f"\n### Exception Occurred: {str(e)} ###")
        print(traceback.format_exc())
        return JsonResponse({'error': 'Internal server error'}, status=500)




def get_expenses_series_by_category(request, start_date, today):
    expenses = Expense.objects.filter(owner=request.user, date__gte=start_date, date__lte=today)

    category_dataframes = defaultdict(pd.DataFrame)

    for expense in expenses:
        category = expense.category
        expense_df = pd.DataFrame({
            'date': [expense.date],
            'amount': [float(expense.amount)]
        })
        category_dataframes[category] = pd.concat([category_dataframes[category], expense_df], ignore_index=True)

    return dict(category_dataframes)


def group_data_by_interval(category_dataframes, interval):
    for category, df in category_dataframes.items():
        df['date'] = pd.to_datetime(df['date'])
        group_by = DEFAULT_DAYS_IN_TIME_INTERVALS[interval][1]
        df_grouped = df.resample(group_by, on='date').sum()
        category_dataframes[category] = df_grouped

    return category_dataframes


def build_datasets_for_total_chart(request, start_date, today, interval):
    data = get_expenses_series_by_category(request, start_date, today)
    data = group_data_by_interval(data, interval)

    datasets = []
    for category, df in data.items():
        datasets.append({
            'label': category,
            'data': df['amount'].tolist(),
            'borderWidth': 1,
        })

    labels = data[next(iter(data))].index.strftime('%Y-%m').tolist() if data else []
    response_data = {'datasets': datasets, 'labels': labels}
    return response_data
