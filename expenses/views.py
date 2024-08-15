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

from configuration.settings import FILTER_BY_OWNER

@login_required(login_url='/authentication/login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    categories = Category.objects.all()
    accounts = Account.objects.all()
    userpreferences = UserPreferences.objects.get(user=request.user)
    
    search_text = request.GET.get('search', '')  # Capture searchText from query parameters

    # Determine the base queryset depending on ownership filter
    expenses = Expense.objects.filter(owner=request.user) if FILTER_BY_OWNER else Expense.objects.all()

    # Apply filtering if searchText is present
    if search_text:
        expenses = expenses.filter(
            Q(amount__icontains=search_text) |
            Q(description__icontains=search_text) |
            Q(category__icontains=search_text) |
            Q(account__icontains=search_text)
        )

    paginator = Paginator(expenses, 2)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'accounts': accounts,
        'expenses': expenses,
        'userpreferences': userpreferences,
        'page_obj': page_obj,
        'search_text': search_text
    }
    return render(request, 'expenses/expenses.html', context)



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

        messages.success(request, 'Expense added successfully')
        return redirect('expenses')
    

def edit_expense(request, id):
    expense=Expense.objects.get(pk=id)
    categories = Category.objects.all()
    accounts = Account.objects.all()
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

        messages.success(request, 'Expense updated successfully')
        return redirect('expenses')
    
@csrf_exempt
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense deleted successfully')
    return redirect('expenses')

@csrf_exempt
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText', '')

        # Determine the base queryset depending on ownership filter
        expenses = Expense.objects.filter(owner=request.user) if FILTER_BY_OWNER else Expense.objects.all()

        # Apply filtering across multiple fields using Q objects
        expenses_filtered = expenses.filter(
            Q(amount__icontains=search_str) |
            Q(description__icontains=search_str) |
            Q(category__icontains=search_str) |
            Q(account__icontains=search_str)
        )

        expenses_list = [
            {
                'id': expense.id,
                'owner': expense.owner.username,  
                'date': expense.date.strftime('%Y-%m-%d'),
                'description': expense.description,
                'category': expense.category,
                'account': expense.account,
                'amount': str(expense.amount),
            }
            for expense in expenses_filtered
        ]

        return JsonResponse({'expenses': expenses_list, 'searchText': search_str})