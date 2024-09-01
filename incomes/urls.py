from django.urls import path
from . import views

urlpatterns = [
    path('incomes', views.index, name='incomes'),
    path('add-income', views.add_income, name='add-incomes'),
    path('edit-income/<int:id>', views.edit_income, name='edit-income'), 
    path('delete-income/<int:id>', views.delete_income, name='delete-income'),
    path('incomes-summary', views.incomes_summary, name='incomes-summary'),
    
    #Endpoints
    path('get_incomes_by_category/<str:interval>', views.get_incomes_by_category, name='get_incomes_by_category'),
]
