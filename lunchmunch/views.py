import dateparser
import pytz

from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, render, redirect

from .forms import EventForm, ProfileForm, GroupForm
from .models import Event, Group

User = get_user_model()
tz = pytz.timezone('America/Chicago')


def home(request):
    template_name = "lunchmunch/home.html"
    context = {}
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
