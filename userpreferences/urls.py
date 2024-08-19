from django.urls import path
from . import views

urlpatterns = [
    path('general-preferences/', views.general_preferences, name='general-preferences'),
    path('add-category-or-account/', views.add_category_or_account, name='add-category-or-account'),
    path('delete-category-or-account/', views.delete_category_or_account, name='delete-category-or-account'),
]
