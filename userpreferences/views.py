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
def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)

    if request.method == "POST":
        currency = request.POST.get('currency')
        if currency:
            user_preferences.currency = currency
            user_preferences.currency_code = user_preferences.currency.split(' - ')[0] if user_preferences.currency else ''
            user_preferences.save()
            messages.success(request, 'Changes saved')
            return redirect('general-preferences')
        else:
            messages.error(request, 'Please select a currency')


    return render(request, 'preferences/general-preferences.html', {
        'currencies': currency_data,
        'user_preferences': user_preferences,
    })
