import dateparser
import datetime

from django import forms

from .models import Event, Group, GroupInvite, LunchMunchProfile


class ProfileForm(forms.ModelForm):

    class Meta:
        model = LunchMunchProfile
        exclude = ['user', 'favorite_users', ]


class EventForm(forms.Form):

    at = forms.CharField(max_length=248, required=True)

    class Meta:
        model = Event
        fields = ('at',)


class GroupInviteForm(forms.Form):
    receiver_username = forms.CharField(max_length=248)

    class Meta:
        fields = ('receiver_username',)


class GroupForm(forms.ModelForm):
    name = forms.CharField(max_length=248)

    class Meta:
        model = Group
        fields = ('name', 'event_starting_seconds', 'in_progress_seconds',
                  'vetoing_seconds_per_user', 'completing_seconds')
