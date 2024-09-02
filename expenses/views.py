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


@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_expenses_by_category(request, interval, calculation_type="total"):
    today = datetime.date.today()
    delta_days = DEFAULT_DAYS_IN_TIME_INTERVALS[interval][0]
    start_date = today - datetime.timedelta(days=delta_days)

    expenses = Expense.objects.filter(owner=request.user, date__gte=start_date, date__lte=today)
    
    result = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def calculate_total(request, start_date, today, interval):
        return build_datasets_for_total_chart(request, start_date, today, interval)

    def calculate_mean(category):
        return expenses.filter(category=category).aggregate(mean_amount=Avg('amount'))['mean_amount'] or 0

    def calculate_proportion(category):
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 1
        category_total = expenses.filter(category=category).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        return (category_total / total_expense) * 100 if total_expense > 0 else 0

    # Define the calculation function map with lambdas for category-specific calculations
    calculation_function_map = {
        "total": lambda: calculate_total(request, start_date, today, interval),
        "mean": lambda category: calculate_mean(category),
        "proportions": lambda category: calculate_proportion(category),
    }

    # Retrieve the calculation function based on calculation_type
    calculation_function = calculation_function_map.get(calculation_type, lambda: calculate_total(request, start_date, today, interval))

    if calculation_type == "total":
        # If calculation_type is "total", execute the function without a category
        result = calculation_function()
    else:
        # For "mean" and "proportions", apply the function per category
        result = {category: calculation_function(category) for category in category_list}

    # Return result as JSON response
    return JsonResponse({'expenses_by_category': result}, safe=False)

def get_expenses_series_by_category(request, start_date, today, interval):
    expenses = Expense.objects.filter(owner=request.user, date__gte=start_date, date__lte=today)

    # Create a dictionary to store the dataframes
    category_dataframes = defaultdict(pd.DataFrame)

    # Iterate over the expenses and populate the dictionary
    for expense in expenses:
        category = expense.category
        # Create a dataframe with the date and amount of the current expense
        expense_df = pd.DataFrame({
            'date': [expense.date],
            'amount': [float(expense.amount)]  # Convert Decimal to float
        })
        # Append the current expense dataframe to the category's dataframe
        category_dataframes[category] = pd.concat([category_dataframes[category], expense_df], ignore_index=True)

    # Convert defaultdict to a regular dictionary
    category_dataframes = dict(category_dataframes)

    return category_dataframes

def group_data_by_interval(category_dataframes, interval):
    for category, df in category_dataframes.items():
        # Ensure the 'date' column is a datetime type
        df['date'] = pd.to_datetime(df['date'])
        group_by = DEFAULT_DAYS_IN_TIME_INTERVALS[interval][1]

        df_grouped = df.resample(group_by, on='date').sum()

        # Update the dictionary with the grouped DataFrame
        category_dataframes[category] = df_grouped

    return category_dataframes

def build_datasets_for_total_chart(request, start_date, today, interval):
    data = get_expenses_series_by_category(request, start_date, today, interval)
    data = group_data_by_interval(data, interval)

    # Debugging: Print the data to check its structure
    print("Grouped Data:", data)
    
    # Prepare datasets for Chart.js
    datasets = []
    for category, df in data.items():
        # Debugging: Print the dataframe for each category
        print(f"Data for category {category}:", df)
        
        datasets.append({
            'label': category,
            'data': df['amount'].tolist(),  # List of amounts grouped by interval
            'borderWidth': 1,
        })

    # Extract the labels (e.g., months, weeks) for the x-axis
    # Ensure the index is not empty
    if data:
        labels = data[next(iter(data))].index.strftime('%Y-%m').tolist()
        # Debugging: Print labels to ensure they are correct
        print("Labels:", labels)
    else:
        labels = []

    response_data = {'datasets': datasets, 'labels': labels}
    return response_data
