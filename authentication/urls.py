from .views import RegistrationView
from django.urls import path

urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),
    path('login', RegistrationView.as_view(), name='login'),
    path('reset-password', RegistrationView.as_view(), name='reset-password'),
    path('set-newpassword', RegistrationView.as_view(), name='set-newpassword'),
]