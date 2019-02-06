from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name="lunchmunch_home"),

    path('signup/', views.signup, name="signup"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(),
         {'next_page': '/'}, name='logout'),

    path('account/', views.account, name="account"),
    path('account/edit/', views.account_edit, name="account_edit"),
    path('account/preferences/', views.preferences, name="preferences"),
    path('account/<username>/', views.account, name="account"),
    path('account/<username>/favorite/', views.favorite, name="favorite"),

    path('group/create/', views.group_form, name="group_form"),
    path('group/<code>/edit/', views.group_form, name="group_form"),
    path('group/<code>/', views.group, name="group"),
    path('group/<code>/event/', views.group_event, name="group_event"),
    path('group/', views.groups, name="groups"),
]
