from django.urls import path
from . import views

urlpatterns = [
    #Views
    path('expenses', views.index, name='expenses'),
    path('add-expense', views.add_expense, name='add-expenses'),
    path('edit-expense/<int:id>', views.edit_expense, name='edit-expense'), 
    path('delete-expense/<int:id>', views.delete_expense, name='delete-expense'),
    path('expenses-summary', views.expenses_summary, name='expenses-summary'),

    #Endpoints
    path('get_expenses_by_category/<str:interval>', views.get_expenses_by_category, name='get_expenses_by_category'),
            
]
