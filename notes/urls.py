from django.urls import path, include

from . import views

urlpatterns = [
    path('add_note/', views.add_note, name="add_note"),
    path('edit_note/<id>/', views.edit_note, name="edit_note"),
    path('resolve_note/<id>/', views.resolve_note, name="resolve_note"),
    path('add_comment/<id>/', views.add_comment, name="add_comment"),
    path('resolve_comment/<id>/', views.resolve_comment, name="resolve_comment"),
]
