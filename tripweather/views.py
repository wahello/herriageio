import datetime
import json
import pytemperature
import requests
import simplejson

from mapbox import Geocoder

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect, render_to_response

from .forms import StartLocForm, EndLocForm, TripForm
from .models import Trip


def check_weather(request, unique_id=None):
    template_name = 'tripweather/tripweather.html'
    trip_form = TripForm(request.POST or None)

    if unique_id and len(unique_id) > 12 and Trip.objects.filter(unique_id=unique_id).exists():
        trip = Trip.objects.filter(unique_id=unique_id).first()
    else:
        unique_id = None
        trip = None

    s_response = {}

    if request.method == "POST" or trip:
        if trip_form.is_valid() or trip:
            if trip:
                s_response = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?APPID=152e2a47ac3c0d92b92e386a722f8217&q=" + trip.start_loc)
                e_response = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?APPID=152e2a47ac3c0d92b92e386a722f8217&q=" + trip.end_loc)
            else:
                s_response = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?APPID=152e2a47ac3c0d92b92e386a722f8217&q=" + trip_form.cleaned_data['start_loc'])
                e_response = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?APPID=152e2a47ac3c0d92b92e386a722f8217&q=" + trip_form.cleaned_data['end_loc'])

            s_response = s_response.json()

            e_response = e_response.json()

            duration = str(datetime.timedelta(seconds=float(requests.get("https://api.mapbox.com/directions-matrix/v1/mapbox/driving/" +
                                                                         str(s_response['coord']['lon']) + "," + str(s_response['coord']['lat']) + ";" +
                                                                         str(e_response['coord']['lon']) + "," + str(e_response['coord']['lat']) +
                                                                         "?access_token=pk.eyJ1IjoiY2hhbmNlaGVycmlhZ2UiLCJhIjoiY2pqdGdyZGM3MzZlcjN3cXE4bDVsb3hjdSJ9.3SfOp7dq5RDZLgUPp05HqQ").json()['durations'][0][1]))).split('.')[0]

            s_cur_temp = pytemperature.k2f(s_response['main']['temp'])
            e_cur_temp = pytemperature.k2f(e_response['main']['temp'])

            trip_notes = 'Looks like your trip will be clear and nice. Drive safe!'
            if e_cur_temp < s_cur_temp:
                trip_notes = 'Oooohhhh. Looks like {0} is a little bit cooler than {1}. Safe travels!'.format(
                    s_response['name'], e_response['name'])

            context = {
                'trip_form': trip_form,
                'trip': trip,

                'center_lon': sum([s_response['coord']['lon'], e_response['coord']['lon']]) / 2,
                'center_lat': sum([s_response['coord']['lat'], e_response['coord']['lat']]) / 2,

                # duration.durations.0.1
                'duration': duration,
                'trip_notes': trip_notes,

                's_response': s_response,
                's_cur_temp': str(s_cur_temp) + ' F°',
                'e_response': e_response,
                'e_cur_temp': str(e_cur_temp) + ' F°',
            }
            return render(request, template_name, context)

    context = {
        'trip_form': trip_form,
    }
    return render(request, template_name, context)


def save_trip(request):
    unique_id = request.GET.get('unique_id', None)
    trip_name = request.GET.get('trip_name', None)
    start_loc = request.GET.get('start_loc', None)
    end_loc = request.GET.get('end_loc', None)

    print(unique_id, trip_name, start_loc, end_loc)

    if unique_id and len(unique_id) > 5:
        trip = Trip.objects.get(unique_id=str(unique_id))
        if trip_name != trip.name:
            trip.name = trip_name
            trip.save()
    else:
        trip = Trip.objects.create(
            name=trip_name,
            start_loc=start_loc,
            end_loc=end_loc
        )

    data = {
        "unique_id": trip.unique_id,
        "name": trip.name,
        "start_loc": trip.start_loc,
        "end_loc  ": trip.end_loc,
        "url" 		: trip.get_absolute_url(),
    }

    return JsonResponse(data)


def delete_trip(request, unique_id=None):
    trip = get_object_or_404(Trip, unique_id=unique_id)
    trip.deleted = True
    trip.save()
    return redirect('check_weather')
