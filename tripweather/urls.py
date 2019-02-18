from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from .views import home, delete_trip, save_trip

urlpatterns = [
    path('<unique_id>/delete/', delete_trip, name="delete_trip"),
    path('', home, name="home"),
    path('save/', save_trip, name="save_trip"),
    path('<unique_id>/', home, name="home"),
]
