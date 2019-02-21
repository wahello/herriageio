from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_hosts import reverse

User = get_user_model()


class Note(models.Model):
    resolved = models.BooleanField(default=False)
    author = models.ForeignKey(
        User, blank=False, null=False, on_delete=models.CASCADE)

    message = models.TextField(blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    parent_id = models.PositiveIntegerField(
        default=None, blank=True, null=True)

    def edit_note_url(self):
        return reverse('edit_note', host="notes", kwargs={'id': self.id})

    def resolve_note_url(self):
        return reverse('resolve_note', host="notes", kwargs={'id': self.id})

    @property
    def get_content_type(self):
        instance = self
        return ContentType.objects.get_for_model(instance.__class__)

    def children(self):
        return Note.objects.filter(parent_id=self.id)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['resolved', '-created_at']


class Comment(models.Model):
    resolved = models.BooleanField(default=False)
    author = models.ForeignKey(
        User, blank=False, null=False, on_delete=models.CASCADE)

    message = models.TextField(blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['-resolved', '-created_at']
