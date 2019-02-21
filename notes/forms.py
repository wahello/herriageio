from django.forms.formsets import BaseFormSet
from django import forms

from .models import Note


class NoteForm(forms.ModelForm):
    author = forms.CharField(
        label="",
        required=False
    )

    message = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Write your message...',
            }))

    class Meta:
        model = Note
        fields = ('author', 'message')
