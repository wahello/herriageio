from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name="birthdate_home"),
    path('about/', views.about, name="birthdate_about"),
    path('features/', views.features, name="birthdate_features"),
    path('pricing/', views.pricing, name="birthdate_pricing"),

    path('log-in/', views.log_in, name="birthdate_log_in"),
    path('sign-up/', views.sign_up, name="birthdate_sign_up"),
    path('log-out/', views.log_out, name="birthdate_log_out"),

    path('dashboard/', views.dashboard, name="birthdate_dashboard"),
    path('dashboard/template/<public_key>/', views.template, name="birthdate_template"),
]
