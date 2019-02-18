from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf.urls import url

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    url(r'^oauth/', include('social_django.urls', namespace='social')),
    path('signup/', views.signup_view, name="signup_view"),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('join/<child_app_label>/', views.join_child_app, name="join_child_app"),
    path('settings/<profile_host_name>/', views.settings, name='settings'),
    path('settings/', views.settings, name='settings'),
    url(r'^settings/password/$', views.password, name='password'),

    path("", views.home, name="home")
]
