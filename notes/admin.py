from django.contrib import admin

from .models import Comment, Note

admin.site.register(Comment)
admin.site.register(Note)
