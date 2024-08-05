from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site    
from .utils import token_generator

class EmailValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'}, status=400)
    
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Email is used, please choose another one'}, status=409)

        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error':'Username should only contain alphanumeric characters'}, status=400)
    
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Username is used, please choose another one'}, status=409)

        return JsonResponse({'username_valid': True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request, "The password is too short!")
                    return render(request, 'authentication/register.html', context)
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={'uidb64':uidb64, 
                                                    'token':token_generator.make_token(user)})
                activate_url= f'http://{domain}{link}'

                email = EmailMessage(
                    'FinanceWebApp - Activate your account',
                    f'Hello {username}!, please activate your user by clicking here:/n {activate_url}',
                    'franciscocucullu@gmail.com',
                    [email]
                    )

                email.send(fail_silently=False)
                
                
                messages.success(request, "Account successfully created!")
                return render(request, 'authentication/register.html')
            
        #messages.success(request, 'Success')
        #messages.warning(request, 'Warning')
        #messages.info(request, 'Info')
        #messages.error(request, 'Error')
        return render(request, 'authentication/register.html')
    
class VerificationView(View):
    def get(self, request, uidb64, token):
        return redirect('login')