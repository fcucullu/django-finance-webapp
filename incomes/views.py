from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .models import Income, Category, Account
from userpreferences.models import UserPreferences
from django.contrib import messages
from decimal import Decimal
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db.models import Q

from configuration.settings import FILTER_BY_OWNER

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    categories = user_preferences.categories_incomes
    accounts = user_preferences.accounts
    search_text = request.GET.get('search', '')  # Capture searchText from query parameters

    # Determine the base queryset depending on ownership filter
    incomes = Income.objects.filter(owner=request.user) if FILTER_BY_OWNER else Income.objects.all()

    # Apply filtering if searchText is present
    if search_text:
        incomes = incomes.filter(
            Q(amount__icontains=search_text) |
            Q(description__icontains=search_text) |
            Q(category__icontains=search_text) |
            Q(account__icontains=search_text)
        )

    incomes = incomes.order_by('-date')

    paginator = Paginator(incomes, user_preferences.rows_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'accounts': accounts,
        'incomes': incomes,
        'user_preferences': user_preferences,
        'page_obj': page_obj,
        'search_text': search_text
    }
    return render(request, 'incomes/incomes.html', context)

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_income(request):
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    categories = user_preferences.categories_incomes
    accounts = user_preferences.accounts
    context = {
        'categories': categories,
        'accounts': accounts,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'incomes/add_income.html', context)

    if request.method == 'POST':
        date = request.POST.get('date', '')
        description = request.POST.get('description', '')
        amount = request.POST.get('amount', '').replace(',','.')
        try:
            amount_decimal = Decimal(amount).quantize(Decimal('0.01'))
        except:
            messages.error(request, 'Amount is invalid')
            return render(request, 'incomes/add_income.html', context)

        category = request.POST.get('category', '')
        account = request.POST.get('account', '')

        is_invalid_input = not all([date, description, amount, category, account])
        is_invalid_category = category == "--- Select Category ---"
        is_invalid_account = account == "--- Select Account ---"
        conditions = is_invalid_input or is_invalid_category or is_invalid_account

        if conditions:
            messages.error(request, 'All fields are mandatory')
            return render(request, 'incomes/add_income.html', context)

        Income.objects.create(
            owner=request.user,
            date=date,
            description=description,
            amount=amount_decimal,
            category=category,
            account=account
        )

        messages.success(request, 'Income added successfully')
        return redirect('incomes')
    

def edit_income(request, id):
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    income = Income.objects.get(pk=id)
    categories = user_preferences.categories_incomes
    accounts = user_preferences.accounts
    context = {
        'income': income,
        'categories': categories,
        'accounts': accounts,
        'values': income,
    }
    
    if request.method == 'GET':
        return render(request, 'incomes/edit_income.html', context)
    
    if request.method == 'POST':
        date = request.POST.get('date', '')
        description = request.POST.get('description', '')
        amount = request.POST.get('amount', '').replace(',','.')
        try:
            amount_decimal = Decimal(amount).quantize(Decimal('0.01'))
        except:
            messages.error(request, 'Amount is invalid')
            return render(request, 'incomes/edit_income.html', context)

        category = request.POST.get('category', '')
        account = request.POST.get('account', '')

        is_invalid_input = not all([date, description, amount, category, account])
        is_invalid_category = category == "--- Select Category ---"
        is_invalid_account = account == "--- Select Account ---"
        conditions = is_invalid_input or is_invalid_category or is_invalid_account

        if conditions:
            messages.error(request, 'All fields are mandatory')
            return render(request, 'incomes/edit_income.html', context)

        income.owner=request.user
        income.date=date
        income.description=description
        income.amount=amount_decimal
        income.category=category
        income.account=account
        income.save()

        messages.success(request, 'Income updated successfully')
        return redirect('incomes')
    
@csrf_exempt
def delete_income(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income deleted successfully')
    return redirect('incomes')

