from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

if settings.DEFAULT_REDIRECT_URL:
    DEFAULT_REDIRECT_URL = settings.DEFAULT_REDIRECT_URL
else:
    DEFAULT_REDIRECT_URL = ".moproblems.io"


def wildcard_redirect(request, path=None):
    new_url = DEFAULT_REDIRECT_URL
    if path is not None:
        new_url = DEFAULT_REDIRECT_URL + "/" + path
    return redirect(new_url)
