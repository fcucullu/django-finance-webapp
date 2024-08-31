from django.urls import path
from . import views

urlpatterns = [
    path('expenses', views.index, name='expenses'),
    path('add-expense', views.add_expense, name='add-expenses'),
    path('edit-expense/<int:id>', views.edit_expense, name='edit-expense'), 
    path('delete-expense/<int:id>', views.delete_expense, name='delete-expense'),
    path('expense-category-summary', views.expense_category_summary, name='expense-category-summary'),
    path('expenses_summary', views.expenses_summary, name='expenses_summary')        
]
