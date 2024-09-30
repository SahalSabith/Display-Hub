from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login as authLogin,authenticate,logout as authlogout
import random,smtplib
from email.message import EmailMessage
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decouple import config
from userProfile.models import Wallet,Transaction

# Create your views here.
@never_cache
def signIn(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return JsonResponse({'success': True, 'redirect_url': '/admin/login/'})
        else:
            return JsonResponse({'success': True, 'redirect_url': '/'})

    if request.POST:
        userName = request.POST.get('userName')
        password = request.POST.get('password')
        user = authenticate(request, username=userName, password=password)
        if user:
            authLogin(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/'})
        else:
            messages.error(request, 'Invalid Username or Password')
            return JsonResponse({'success': False, 'messages': 'Invalid Username or Password'})

    return render(request, 'authenticate.html')


@never_cache
def signUp(request):
    if request.method == 'POST':
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        userName = request.POST.get('userName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')

        existUser = User.objects.filter(username=userName)
        if existUser:
            messages.error(request, 'Username already exists')
            return JsonResponse({'success': False, 'messages': '<p>Username already exists</p>'})
        else:
            if password == confirmPassword:
                # Save user logic here
                request.session['username'] = userName
                request.session['email'] = email
                request.session['password'] = confirmPassword
                request.session['firstName'] = firstName
                request.session['lastName'] = lastName
                return JsonResponse({'success': True, 'redirect_url': '/signIn/emailOtpVerification/'})
            else:
                messages.error(request, "Passwords don't match")
                return JsonResponse({'success': False, 'messages': "<p>Passwords don't match</p>"})

    return JsonResponse({'success': False, 'messages': "<p>Invalid request method</p>"})

@never_cache
def sendOtp(request):
    otp = ""
    if request.POST:
        toEmail = request.session.get('email')
        for digit in range(6):
            otp += str(random.randint(1,9))
        request.session['otp'] = otp
        request.session['purpose'] = 'emailVerification'
        print(otp)
        try:
            server = smtplib.SMTP('smtp.gmail.com',587)
            server.starttls()

            adminEmail = config('adminEmail')
            server.login(adminEmail,config('adminPassword'))

            print(toEmail)

            msg = EmailMessage()
            msg['Subject'] = "Display Hub OTP Verification"
            msg['From'] = adminEmail
            msg['To'] = toEmail
            msg.set_content("Your OTP is: " + otp)
            server.send_message(msg)
            server.quit()
            print("sccefullty sent")
        except Exception as e:
                print(f"Failed: {e}")
        
    return render(request,'emailVerification.html')

@never_cache
def forgotPassword(request):
    otp = ""
    mailSent = False
    toEmail = None
    if request.POST:
        toEmail = request.POST.get('email')
        existEmail = User.objects.filter(email = toEmail)
        if existEmail:
            for digit in range(6):
                otp += str(random.randint(1,9))

            request.session['otp'] = otp
            request.session['userEmail'] = toEmail
            request.session['purpose'] = 'passwordReset'
            print(otp)
            try:
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.starttls()

                adminEmail = config('adminEmail')
                server.login(adminEmail,config('adminPassword'))

                print(toEmail)

                msg = EmailMessage()
                msg['Subject'] = "Display Hub OTP Verification"
                msg['From'] = adminEmail
                msg['To'] = toEmail
                msg.set_content("Your OTP is: " + otp)
                server.send_message(msg)
                server.quit()
                print("sccefullty sent")
                mailSent = True
            except Exception as e:
                print(f"Failed: {e}")
        else:
            messages.error(request,"No User Found")
    context = {
                'mailSent' : mailSent,
                'toEmail' : toEmail
            }
    return render(request,'forgotPassword.html',context)

@never_cache
def verifyPassword(request):
    if request.POST:
        userOtp = request.POST.get('otp')
        print(userOtp)
        generatedOtp = request.session.get('otp')
        print(generatedOtp)
        if userOtp == generatedOtp:
            print("perfect")
            if request.session.get('purpose') == 'passwordReset':
                request.session['verified'] = True
                return redirect('resetPassword')
            else:
                return redirect('resetPassword')
        else:
            messages.error(request,"OTP does'nt Match")
            return redirect('emailVerification')
    return render(request,'forgotPassword.html')

@never_cache
def verifyEmail(request):
    if request.method == 'POST':
        userOtp = request.POST.get('otp')
        generatedOtp = request.session.get('otp')
        
        if userOtp == generatedOtp:
            if request.session.get('purpose') == 'emailVerification':
                username = request.session.get('username')
                email = request.session.get('email')
                password = request.session.get('password')
                firstName = request.session.get('firstName')
                lastName = request.session.get('lastName')
                newUser = User.objects.create_user(username=username, email=email, password=password, first_name=firstName, last_name=lastName)
                newUser.save()
                Wallet.objects.create(userId=newUser)
                return JsonResponse({'success': True, 'redirect_url': '/signIn/'})
            else:
                return JsonResponse({'success': True, 'redirect_url': '/signIn/resetPassword/'})
        else:
            return JsonResponse({'success': False, 'error_message': "OTP doesn't match"})

    return render(request, 'emailVerification.html')


@never_cache
def resetPassword(request):
    if request.session.get('verified') == True:
        if request.POST:
            newPassword = request.POST.get('newPassword')
            confirmPassword = request.POST.get('confirmPassword')
            userEmail = request.session.get('userEmail')

            if newPassword == confirmPassword:
                user = User.objects.get(email = userEmail)
                user.set_password(confirmPassword)
                user.save()
                return redirect('signIn')
            else:
                messages.error(request,"Password doest'nt Match")
    else:
        return redirect('signIn')
    return render(request,'resetPassword.html')

@never_cache
def logout(request):
    authlogout(request)
    return redirect('/')

from django.contrib.auth import authenticate, login as authLogin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

@never_cache
def adminLogin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin')
        else:
            return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            if user.is_superuser:
                authLogin(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/admin/'})
            else:
                error_message = "User can't login in Admin Panel"
                return JsonResponse({'success': False, 'error_message': error_message})
        else:
            error_message = "Username and Password don't match"
            return JsonResponse({'success': False, 'error_message': error_message})

    return render(request, 'adminLogin.html')

@never_cache
@login_required(login_url='/admin/login')
def block(request,uId):
    user = get_object_or_404(User,id=uId)
    user.is_active = not user.is_active
    user.save()
    print("activatetion")
    return redirect('allUsers')