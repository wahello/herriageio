import dateparser
import pytz

from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from profile_handling.models import Profile
from .forms import EventForm, ProfileForm, GroupForm
from .models import Event, Group

User = get_user_model()
tz = pytz.timezone('America/Chicago')


def home(request):
    return redirect('launchpad')

    template_name = "lunchmunch/home.html"
    context = {}
    return render(request, template_name, context)


def launchpad(request, redirect_confirmation=None):
    template_name = "lunchmunch/launchpad.html"

    if request.user.is_authenticated and Profile.objects.filter(user=request.user, host="lunchmunch").exists():
        redirect_confirmation = "thank-you"

    if request.method == "POST" and redirect_confirmation is None:
        email = request.POST.get('email_address')
        user, created = User.objects.get_or_create(email=email, username=email)
        if created:
            Profile.objects.create(user=user, host='lunchmunch')
            messages.success(
                request, "%s has been created and has been added to the Lunch o' Munch community." % (user.email))
        elif user is not None:
            if not Profile.objects.filter(user=user, host="lunchmunch").exists():
                Profile.objects.create(user=user, host='lunchmunch')
                messages.success(
                    request, "%s has been added to the Lunch o' Munch community." % (user.email))

        if user is not None:
            return redirect(reverse('launchpad', kwargs={'redirect_confirmation': 'thank-you'}))
        else:
            redirect_confirmation = None
            messages.error(request,
                           'There was an error adding you to our community. ☹️')

    context = {
        'redirect_confirmation': redirect_confirmation,
    }
    return render(request, template_name, context)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'lunchmunch/signup.html', {'form': form})


@login_required
def account(request, username=None):
    template_name = "lunchmunch/account.html"

    if username and User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
    else:
        user = request.user

    context = {
        'user': user,
    }
    return render(request, template_name, context)


@login_required
def account_edit(request):
    template_name = "lunchmunch/form.html"
    form = ProfileForm(request.POST or None,
                       request.FILES or None, instance=request.user.profile)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(
                request, 'The changes to your account have been saved.')
            return redirect(request.user.profile.get_absolute_url())

    context = {
        "form": form,
    }

    return render(request, template_name, context)


@login_required
def favorite(request, username):
    favorite_user = get_object_or_404(User, username=username)
    favorited = request.user.profile.favorite_user(favorite_user)

    if favorited:
        messages.success(request, "%s has been favorited." %
                         (favorite_user.username))
    else:
        removed = request.user.profile.unfavorite_user(favorite_user)
        if removed:
            messages.success(request, "%s has been unfavorited." %
                             (favorite_user.username))

    return redirect(favorite_user.profile.get_absolute_url())


def group_event(request, code):
    template_name = "lunchmunch/event.html"
    group = get_object_or_404(Group, code=code)
    event = group.next_event
    form = None

    if not event:
        form = EventForm(request.POST or None)

        if request.method == "POST":
            if form.is_valid():
                if not group.next_event:
                    event = Event.objects.create(
                        group=group,
                        at=tz.localize(dateparser.parse(
                            request.POST.get('at')), is_dst=True),
                        status="upcoming",
                    )
                    messages.success(request, 'Event has been scheduled.')
                else:
                    messages.error(
                        request, 'This group already has an upcoming event scheduled.')
            else:
                messages.error(request, 'Event scheduler form is not valid.')
            return redirect('group_event', code=group.code)

    context = {
        'group': group,
        'event': event,
        'form': form,
    }

    return render(request, template_name, context)


@login_required
def group(request, code):
    template_name = "lunchmunch/group.html"
    group = get_object_or_404(Group, code=code)

    context = {
        'group': group
    }

    return render(request, template_name, context)


@login_required
def group_form(request, code=None):
    template_name = "lunchmunch/form.html"
    form = GroupForm(request.POST or None)

    if code:
        group = get_object_or_404(Group, code=code)
        form = GroupForm(request.POST or None,
                         request.FILES or None, instance=group)

    if request.method == "POST":
        if form.is_valid():
            group = form.save(commit=False)
            group.leader = request.user
            group.save()
            return redirect(group.get_absolute_url())

    context = {
        'form': form,
    }

    return render(request, template_name, context)


@login_required
def groups(request):
    template_name = "lunchmunch/groups.html"

    if request.user.profile.has_group:
        groups = request.user.profile.groups
    else:
        return redirect('group_form')

    context = {
        "groups": groups,

    }
    return render(request, template_name, context)


def preferences(request):
    # preferences formset from question as label and answer as the input.
    template_name = "lunchmunch/preferences.html"

    context = {
        'formset': None,
    }

    return render(request, template_name, context)
