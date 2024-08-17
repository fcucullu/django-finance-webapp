from . import views
from django.urls import path

urlpatterns = [
    path('general-preferences', views.general_preferences, name="general-preferences")
]
