from django.shortcuts import render, redirect
import os
import json
from django.conf import settings
from .models import UserPreferences
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from userpreferences.models import UserPreferences

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def general_preferences(request):
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    # Initialize variables with default values
    categories_expenses = user_preferences.categories_expenses
    categories_incomes = user_preferences.categories_incomes
    accounts = user_preferences.accounts
    
    # Currency configuration
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    # Rows_per_page configuration
    rows_per_page_data = [10, 25, 50, 100]  

    if request.method == "POST":
        currency = request.POST.get('currency', user_preferences.currency)
        rows_per_page = int(request.POST.get('rows_per_page', user_preferences.rows_per_page))
        
        # Get POST data or keep existing values
        categories_expenses = request.POST.getlist('categories_expenses', user_preferences.categories_expenses)
        categories_incomes = request.POST.getlist('categories_incomes', user_preferences.categories_incomes)
        accounts = request.POST.getlist('accounts', user_preferences.accounts)
        
        if currency:
            user_preferences.currency = currency
            user_preferences.currency_code = user_preferences.currency.split(' - ')[0] if user_preferences.currency else ''
        
        user_preferences.rows_per_page = rows_per_page
        user_preferences.categories_expenses = categories_expenses
        user_preferences.categories_incomes = categories_incomes
        user_preferences.accounts = accounts
      
        user_preferences.save()

        messages.success(request, 'Changes saved')
        return redirect('general-preferences')

    return render(request, 'preferences/general-preferences.html', {
        'currencies': currency_data,
        'user_preferences': user_preferences,
        'rows_per_page_data': rows_per_page_data,
        'categories_expenses': categories_expenses,
        'categories_incomes': categories_incomes,
        'accounts': accounts,
    })


@csrf_exempt
@login_required(login_url='/authentication/login')
def add_category_or_account(request):
    try:
        data = json.loads(request.body)
        category_type = data['category_type']
        new_item = data['new_item']
        user_preferences = UserPreferences.objects.get(user=request.user)

        if category_type == 'income':
            user_preferences.categories_incomes.append(new_item)
            user_preferences.categories_incomes.sort(key=str.lower)  # Case-insensitive sort
        elif category_type == 'expense':
            user_preferences.categories_expenses.append(new_item)
            user_preferences.categories_expenses.sort(key=str.lower)  # Case-insensitive sort
        elif category_type == 'account':
            user_preferences.accounts.append(new_item)
            user_preferences.accounts.sort(key=str.lower)  # Case-insensitive sort


        messages.success(request, "Item added successfully")
        user_preferences.save()
        return JsonResponse({'status': 'success'})

    except:
        print(data)
        messages.warning(request, "Item NOT added successfully")
        return JsonResponse({'status': 'failed'})



@csrf_exempt
@login_required(login_url='/authentication/login')
def delete_category_or_account(request):
    try:
        data = json.loads(request.body)
        category_type = data['category_type']
        item = data['item']
        user_preferences = UserPreferences.objects.get(user=request.user)

        if category_type == 'income':
            user_preferences.categories_incomes.remove(item)
        elif category_type == 'expense':
            user_preferences.categories_expenses.remove(item)
        elif category_type == 'account':
            user_preferences.accounts.remove(item)

        messages.success(request, "Item deleted successfully")
        user_preferences.save()
        return JsonResponse({'status': 'success'})

    except:
        messages.warning(request, "Item NOT deleted successfully")
        return JsonResponse({'status': 'failed'})