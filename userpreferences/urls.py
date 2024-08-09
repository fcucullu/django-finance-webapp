from . import views
from django.urls import path

urlpatterns = [
    path('general-preferences', views.index, name="general-preferences")
]
