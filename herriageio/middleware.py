import json

from django.contrib.auth import get_user_model
from django.core import serializers

User = get_user_model()


class UserFieldCompilingMiddleware(object):
    # this is needed to initialize this middleware class.
    def __init__(self, get_response):
        self.get_response = get_response

    # this is called between the calling and displaying of the views.
    def __call__(self, request):
        request.request_user_field_data = serializers.serialize(
            "python", User.objects.filter(id=request.user.id))
        return self.get_response(request)


class GetUserProfiles(object):
    # this is needed to initialize this middleware class.
    def __init__(self, get_response):
        self.get_response = get_response

    # this is called between the calling and displaying of the views.
    def __call__(self, request):
        from profile_handling.models import Profile
        if request.user.is_authenticated:
            request.user_profiles = Profile.objects.filter(user=request.user)
        return self.get_response(request)


class HasProfileForSolution(object):
    # this is needed to initialize this middleware class.
    def __init__(self, get_response):
        self.get_response = get_response

    # this is called between the calling and displaying of the views.
    def __call__(self, request):
        from profile_handling.models import Profile
        request.current_host = str(request.build_absolute_uri().replace(
            "https://", "").replace(
            "http://", "").split(".")[0])

        if request.user.is_authenticated:
            request.user_has_profile_for_solution = Profile.objects.filter(
                user=request.user, host=request.current_host).exists()
            request.profile = Profile.objects.filter(
                user=request.user, host=request.current_host).first()
        else:
            request.user_has_profile_for_solution = False

        return self.get_response(request)
