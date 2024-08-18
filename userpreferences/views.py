from django.shortcuts import render, redirect
import os
import json
from django.conf import settings
from .models import UserPreferences
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def general_preferences(request):
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    #Currency configuration
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    #Rows_per_page configuration
    rows_per_page_data = [10, 25, 50, 100]  

    if request.method == "POST":
        currency = request.POST.get('currency', user_preferences.currency)
        rows_per_page = int(request.POST.get('rows_per_page', user_preferences.rows_per_page))
        if currency:
            user_preferences.currency = currency
            user_preferences.currency_code = user_preferences.currency.split(' - ')[0] if user_preferences.currency else ''
            user_preferences.rows_per_page = rows_per_page
            user_preferences.save()
            messages.success(request, 'Changes saved')
            return redirect('general-preferences')
        else:
            messages.error(request, 'Error, please try again')
            # messages.error(request, 'Please select a currency')


    return render(request, 'preferences/general-preferences.html', {
        'currencies': currency_data,
        'user_preferences': user_preferences,
        'rows_per_page_data': rows_per_page_data,
    })
