from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'birthdate', 'birthdate.urls', name='birthdate'),
    host(r'tripweather', 'tripweather.urls',
         name='tripweather'),
    host(r'lunchmunch', 'lunchmunch.urls',
         name='lunchmunch'),
    host(r'notes', 'notes.urls',
         name='notes'),
    host(r'(?!www).*', 'hostsconf.urls', name='wildcard'),
)
