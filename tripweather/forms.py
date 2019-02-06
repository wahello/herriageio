from django import forms

from .models import Trip


class StartLocForm(forms.Form):
    location = forms.CharField(max_length=24)


class EndLocForm(forms.Form):
    location = forms.CharField(max_length=24)


class TripForm(forms.ModelForm):
    start_loc = forms.CharField(label="", max_length=24, widget=forms.TextInput({
                                'placeholder': 'Departure Location...'}))
    end_loc = forms.CharField(label="", max_length=24, widget=forms.TextInput({
                              'placeholder': 'Arrival Location...'}))

    class Meta:
        model = Trip
        fields = ['start_loc', 'end_loc']
