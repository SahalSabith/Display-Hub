"""
URL configuration for displayHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('signIn/',views.signIn,name='signIn'),
    path('signUp/',views.signUp,name='signUp'),
    path('signIn/forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('account/logout/',views.logout,name='logout'),
    path('admin/login/',views.adminLogin,name='adminLogin'),
    path('signIn/verifyPassword',views.verifyPassword,name='verifyPassword'),
    path('signIn/resetPassword/',views.resetPassword,name='resetPassword'),
    path('emailVerification/',views.sendOtp,name='emailVerification'),
    path('admin/block/<int:uId>/',views.block,name='block'),
    path('signIn/emailOtpVerification/',views.verifyEmail,name="verifiyEmailOtp")
]
