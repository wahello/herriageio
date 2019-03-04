from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import (
    login, authenticate, logout, update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404, render, redirect, render_to_response)

from django_hosts.resolvers import reverse
from social_django.models import UserSocialAuth

from .forms import LoginForm, SignupForm
from profile_handling.forms import ProfileFormForAdmins
from profile_handling.models import Profile


def home(request):
    template_name = "herriageio/home.html"
    context = {}

    return render(request, template_name, context)


def login_view(request):
    template_name = 'herriageio/login.html'
    form = LoginForm(request.POST or None)
    ref_app = request.POST.get('ref_app', request.GET.get('ref_app', None))
    next = request.POST.get('next', request.GET.get('next', None))

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You\'ve logged into your account.')
                if ref_app:
                    return redirect(reverse('home', host=ref_app))
                if next:
                    return HttpResponseRedirect(next)
                return redirect('/')
            else:
                messages.error(
                    request, "The username or password is incorrect.")
        else:
            messages.error(
                request, "The username or password is incorrect.")

    context = {
        "section_header": "Account Access",
        "form": form,
        'ref_app': ref_app,
        'heading': "Hop Into Your Account.",
        'heading_sub_p': 'If you\'ve never created an account you can do so by using your favorite social platform or your email. If you do have an account, continue with what you used the first time',
    }

    return render(request, template_name, context)


def signup_view(request):
    template_name = "herriageio/signup.html"
    ref_app = request.POST.get('ref_app', request.GET.get('ref_app', None))

    ref_app_exists = False
    for value, app in django_settings.CHILD_APPS:
        if not ref_app_exists:
            if ref_app == value:
                ref_app_exists = True

    if not ref_app_exists:
        ref_app = None

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(ref_app=ref_app)
            user = authenticate(username=user.username,
                                password=form.cleaned_data['password2'])
            if user is not None:
                login(request, user)
                messages.success(request, 'You\'ve successfully logged in.')
                if ref_app:
                    return redirect(reverse('home', host=ref_app))
                return redirect('/')
            else:
                messages.error(
                    request, 'Your account could not be created at this time.')
                return redirect('signup_view')
    else:
        form = SignupForm()

    context = {
        'form': form,
        'ref_app': ref_app,

        'heading': 'Sign Up',
        'heading_sub_p': 'Hello 👱 Go ahead and sign up for an account and you will have access to all of our community features for free!',
    }

    return render(request, template_name, context)


def logout_view(request):
    logout(request)
    messages.success(
        request, 'You\'ve successfully logged out of your account.')
    return redirect('/')


@login_required
def settings(request, profile_host_name="www"):
    user = request.user

    mp_host_redirect = request.POST.get(
        'mp_host_redirect', request.GET.get('mp_host_redirect', ''))
    mp_redirect_confirmation = request.POST.get(
        'mp_redirect_confirmation', request.GET.get('mp_redirect_confirmation', ''))
    mp_path = request.POST.get(
        'mp_path', request.GET.get('mp_path', ''))

    if mp_host_redirect and mp_redirect_confirmation and mp_path:
        return redirect(reverse('launchpad', host=mp_host_redirect, kwargs={'redirect_confirmation': mp_redirect_confirmation}))

    ref_app_exists = False
    for value, app in django_settings.CHILD_APPS:
        if not ref_app_exists:
            if profile_host_name == value:
                ref_app_exists = True

    if not ref_app_exists:
        messages.error(
            request, 'You cannot edit a profile for a community that does not exist.')
        return redirect(reverse('home', host='www'))

    if Profile.objects.filter(user=request.user, host=profile_host_name).exists():
        profile = Profile.objects.get(
            user=request.user, host=profile_host_name)
    else:
        messages.error(
            request, 'You do not have a profile for that community.')
        return redirect(reverse('home', host=profile_host_name))

    profile = get_object_or_404(
        Profile, user=request.user, host=profile_host_name)

    profile_form = ProfileFormForAdmins(
        request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST":
        if profile_form.is_valid():
            profile = profile_form.save()
            messages.success(
                request, 'You\'ve updated the settings of your account.')
            return redirect(profile.get_settings_url())

    try:
        github_login = user.social_auth.get(provider='github')
    except UserSocialAuth.DoesNotExist:
        github_login = None

    try:
        twitter_login = user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None

    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    try:
        google_login = user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        google_login = None

    can_disconnect = (user.social_auth.count() >
                      1 or user.has_usable_password())

    return render(request, 'herriageio/settings.html', {
        'github_login': github_login,
        'twitter_login': twitter_login,
        'facebook_login': facebook_login,
        'google_login': google_login,
        'can_disconnect': can_disconnect,
        'profile': profile,
        'profile_form': profile_form,
    })


@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'herriageio/password.html', {'form': form})


def join_child_app(request, child_app_label=None):
    template_name = 'herriageio/join.html'

    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to join a community.')
        return redirect("%s?ref_app=%s" % (reverse('login_view', host='www'), child_app_label))

    if child_app_label is None:
        messages.error(
            request, 'You must specify which community you would like to join.')
        return redirect(reverse('home', host='www'))

    in_apps = False
    for value, app in django_settings.CHILD_APPS:
        if child_app_label == value:
            in_apps = True

    # makes sure they can't join a community that doesn't exist
    if not in_apps:
        messages.error(
            request, 'You have tried to join a community of a solution that doesn\'t exist.')
        return redirect('home')

    # makes sure that they can't have duplicate profiles
    if Profile.objects.filter(user=request.user, host=child_app_label).exists():
        messages.error(
            request, 'You have already joined this solutions community.')
        return redirect(reverse('home', child_app_label))
    # create the profile for the user since they've passed all limits
    else:
        profile = Profile.objects.create(
            user=request.user, host=child_app_label)
        messages.success(request, 'You\'ve joined the community for %s' % (
            child_app_label.title()))
        return redirect(profile.get_absolute_url())

    context = {
        'child_app_label': child_app_label,
        'apps': django_settings.CHILD_APPS,
        'in_apps': in_apps,
    }
    return render(request, template_name, context)
