from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from validate_email import validate_email
from django.contrib import messages, auth
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login


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
                                                    'token':token_generator.generate_token(user)})
                activate_url= f'http://{domain}{link}'

                email = EmailMessage(
                    'FinanceWebApp - Activate your account',
                    f'Hello {username}!, please activate your user by clicking here:/n {activate_url}',
                    'franciscocucullu@gmail.com',
                    [email]
                    )

                email.send(fail_silently=False)
                
                
                messages.success(request, "Account successfully created! Check your email to activate your user")
                return render(request, 'authentication/register.html')
        else:
            messages.error(request, "Introduce your new Username!")
            return render(request, 'authentication/register.html', context)
    
class VerificationView(View):
    def get(self, request, uidb64, token):
        
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                messages.info(request, 'User already activated')
                return redirect('login')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully! Now, please login')
            return redirect('login')
        
        except Exception as ex:
            pass

        return redirect('login')
    
class LoginView(View):
    def get(self, request):
        # Get the 'next' parameter from the URL, default to '/' if not provided
        next_url = request.GET.get('next', '/')
        return render(request, 'authentication/login.html', {'next': next_url})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '/')  # Get the 'next' parameter from the form

        if username and password:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

            if user:
                if user.is_active:
                    user = authenticate(username=username, password=password)
                    if user:
                        auth_login(request, user)
                        messages.success(request, f'Welcome, {user.username}! You are now logged in.')
                        return redirect(next_url)  # Redirect to the 'next' URL
                    else:
                        messages.error(request, 'Invalid credentials, please try again.')
                else:
                    messages.error(request, 'Your account is not active. Please check your email.')
            else:
                messages.error(request, 'Invalid credentials, please try again.')
        else:
            messages.error(request, 'Please fill all fields.')

        return render(request, 'authentication/login.html', {'next': next_url})  # Pass 'next' back to the template
    
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
    

class ResetPassword(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST.get('email')
        context = {'fieldValues': request.POST}  
        user = User.objects.filter(email=email)      
        
        if user:
            
            uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
            domain = get_current_site(request).domain
            link = reverse('set-newpassword', kwargs={'uidb64':uidb64, 
                                                'token':token_generator.generate_token(user[0])})
            reset_url= f'http://{domain}{link}'

            email_body = (
                "Hello,\n\n"
                "It seems you have requested to reset your password. If this was you, please click the link below to proceed:\n\n"
                f"{reset_url}\n\n"
                "If you did not request this, please disregard this email.\n\n"
                "Best regards,\n"
                "FinanceWebApp Team"
            )

            email_object = EmailMessage(
                'FinanceWebApp - Reset password link',
                email_body,
                'franciscocucullu@gmail.com',
                [email]
                )

            email_object.send(fail_silently=False)


        if len(email) > 0 :
            messages.success(request, 'If this email is registered, we have sent you a reset link there.')
        return render(request, 'authentication/reset-password.html', context) 


class SetNewPassword(View):
    def get(self, request, uidb64, token):

        context = {
            'uidb64': uidb64,
            'token': token
            }

        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user, token):
                messages.info(request, 'Link invalid or used. Please request a new one')
                return render(request, 'authentication/reset-password.html', context) 

        except:
            messages.info(request, 'Something went wrong. Try again or ask for a new link.')
            return redirect('login')
        
        return render(request, 'authentication/set-newpassword.html', context) 
    
    def post(self, request, uidb64, token):

        context = {
            'uidb64': uidb64,
            'token': token
        }
                
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/set-newpassword.html', context)

        if len(password) < 6:
            messages.error(request, 'Password is too short.')
            return render(request, 'authentication/set-newpassword.html', context)

        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successfully. Now, please login.')
            return redirect('login')
        except:
            messages.info(request, 'Something went wrong. Try again.')
            return render(request, 'authentication/set-newpassword.html', context)
