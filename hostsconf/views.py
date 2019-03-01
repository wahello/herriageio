from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

if settings.DEFAULT_REDIRECT_URL:
    DEFAULT_REDIRECT_URL = settings.DEFAULT_REDIRECT_URL
else:
    DEFAULT_REDIRECT_URL = "moproblems.io"


def wildcard_redirect(request, path=None):
    new_url = DEFAULT_REDIRECT_URL
    if path is not None:
        # this is the wildcard redirect that is fired when we cannot find a host. So, it will redirect to http://www.localhost:8000/
        # + /path (We don't want the path in this because if we are directing to the wildcard redirect then they've access an unavailable host and we want to send them to the homepage.)
        new_url = "http://www." + DEFAULT_REDIRECT_URL + "/"
    return redirect(new_url)
