import datetime
import django
import pytz
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.shortcuts import redirect
from django.urls import reverse

User = get_user_model()
tz = pytz.timezone('America/Chicago')


class PreferenceProfile(models.Model):
    """ this will be the aggregate of the users profile. """

    pass


class PreferenceQuestion(models.Model):
    """ this will be the questions that are admin-created and used for filtering to determine a happy medium. with pre-defined answer posibilites in choices. """

    # $$$
    # distance radius
    # type of food
    # wait time / dine time
    # rating

    pass


class PreferenceAnswer(models.Model):
    """ the answer they chose. """

    pass


class Group(models.Model):
    users = models.ManyToManyField(User)
    leader = models.ForeignKey(User,
                               default=None,
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL,
                               related_name="leader")
    name = models.CharField(
        max_length=248,
        null=True)
    has_custom_name = models.BooleanField(
        default=False)
    code = models.CharField(
        default=uuid.uuid4().hex[:6].upper(),
        editable=False,
        max_length=6)
    checked_code = models.BooleanField(
        default=False)

    # the queue for users to join the event
    event_starting_seconds = models.PositiveIntegerField(default=30)
    # building list of choices phase
    in_progress_seconds = models.PositiveIntegerField(default=120)
    # veto stage
    vetoing_seconds_per_user = models.PositiveIntegerField(default=15)
    completing_seconds = models.PositiveIntegerField(default=30)

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        ordering = ['name', ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('group', kwargs={"code": self.code})

    @property
    def promote_leader(self):
        self.leader = users.first()
        self.save()

    @property
    def next_event(self):
        from events.models import Event

        if Event.objects.filter(group=self, status="upcoming").exists():
            return Event.objects.filter(group=self, status="upcoming").first()
        return None

    @property
    def events(self):
        from events.models import Event
        return Event.objects.filter(group=self)

    def testing_bulk_import_users(self, user_dictionary):
        for user in user_dictionary:
            self.users.add(user)
        self.save()


@receiver(pre_save, sender=Group)
def pre_group_save(sender, instance, **kwargs):
    """ making sure the object doesn't have the same code as another group. """

    if not instance.id:
        if Group.objects.filter(code=instance.code).exists():
            instance.code = uuid.uuid4().hex[:6].upper()

    """ if the object has been created and we haven't checked the code yet. """
    if instance.id and not instance.checked_code:
        if Group.objects.filter(code=instance.code).count() == 1:
            instance.checked_code = True


@receiver(post_save, sender=Group)
def post_group_create(sender, instance, created, **kwargs):
    """ Checking on the post_save of the group that resulted in the creation of the object. """

    """ Checking to see if the object was just created and if they weren't added to the user dictionary already, then we need to now. """
    if created and instance.leader and instance.users.count() == 0:
        instance.users.add(instance.leader)
        instance.save()


@receiver(post_save, sender=Group)
def post_group_save(sender, instance, **kwargs):
    """ These are things that shoudl still be checked, but not for validation so they are placed in the post_save. """

    """ If the group has a blank name we will count the number of groups that the leader has and then just append 1 additional. EX: Group #1 """
    changed_name = False
    if not instance.name and not instance.has_custom_name and instance.users is not None:
        instance.name = "%s #%s" % ("Group", Group.objects.filter(
            leader=instance.leader).count() + 1)
        changed_name = True
        instance.save()

    """ if we have a leader, but don't have any users in the dictionary. This could only happen from a leader leaving the group or deleting their account. """
    if instance.leader and instance.users is None:
        instance.users.add(instance.leader)
        instance.save()

    """ If the group doesn't have a leader, but does have users in the users dictionary. Then we will promote the first one in the dictionary automatically. """
    if not instance.leader and instuance.users is not None:
        instance.promote_leader()


class GroupEventHours(models.Model):
    group = models.ForeignKey(Group,
                              on_delete=models.CASCADE
                              )

    WEEKDAYS = [
        (1, ("Monday")),
        (2, ("Tuesday")),
        (3, ("Wednesday")),
        (4, ("Thursday")),
        (5, ("Friday")),
        (6, ("Saturday")),
        (7, ("Sunday")),
    ]
    weekday = models.IntegerField(
        choices=WEEKDAYS,
        unique=True
    )
    from_hour = models.TimeField()
    to_hour = models.TimeField()


class GroupInviteManager(models.Manager):
    def by_user(self, user):
        return self.filter(sender=user)

    def to_user(self, user):
        return self.filter(sender=user)

    def get_or_create_invite(self, group, sender, receiver, message="You've been invited to join a new 🍰  Munch group."):
        return self.get_or_create(
            group=group,
            sender=sender,
            receiver=receiver,
            message=message,
            status="active",)

    def has_and_get_invite(self, group, receiver):
        return self.filter(group=group, receiver=receiver, status="active").exists(), self.filter(group=group, receiver=receiver, status="active").first()

    def has_invite(self, group, receiver):
        return self.filter(group=group, receiver=receiver, status="active").exists()

    def get_invite(self, group, receiver):
        return self.filter(group=group, receiver=receiver, status="active").first()


class GroupInvite(models.Model):
    group = models.ForeignKey(Group,
                              on_delete=models.CASCADE)
    sender = models.ForeignKey(User,
                               blank=False,
                               on_delete=models.CASCADE,
                               related_name="group_invite_sender")
    receiver = models.ForeignKey(User,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="group_invite_receiver")
    message = models.TextField(
        blank=True,
        null=True)

    STATUS_CHOICES = (
        ("active", "active"),
        ("declined", "declined"),
        ("accepted", "accepted"),
        ("archived", "archived"),
    )
    status = models.CharField(choices=STATUS_CHOICES,
                              blank=True, null=True, max_length=48)

    created_at = models.DateTimeField(
        auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now_add=True)

    objects = GroupInviteManager()

    class Meta:
        verbose_name = "Group Invite"
        verbose_name_plural = "Group Invite"
        ordering = ['created_at', ]

    def __str__(self):
        return self.receiver.username + " for " + self.group.name

    def accept(self):
        has_invite, invite = GroupInvite.objects.has_and_get_invite(
            group=self.group, receiver=self.receiver)
        if has_invite:
            self.status = "accepted"
            self.group.users.add(self.receiver)
            self.save()

    def decline(self):
        has_invite, invite = GroupInvite.has_and_get_invite(
            group=self.group, receiver=self.receiver)
        if has_invite:
            self.status = "declined"
            self.save()

    def archive(self):
        has_invite, invite = GroupInvite.has_and_get_invite(
            group=self.group, receiver=self.receiver)
        if has_invite:
            self.status = "archived"
            self.save()


class EventManager(models.Manager):
    def next_event_at(self, group):
        return self.filter(group=group).first()


class Event(models.Model):
    group = models.ForeignKey(Group,
                              on_delete=models.CASCADE)

    at = models.DateTimeField(blank=False, null=False)

    STATUS_CHOICES = (
        # the scheduled date is still in the future
        ("upcoming", "upcoming"),
        # building the queue / lobby
        ("starting", "starting"),
        # choose top choices for the day
        ("in_progress", "in_progress"),
        # users vetoing the restaurants they really don't want
        ("vetoing", "vetoing"),
        # system choosing final best option
        ("completing", "completing"),
        # event has been completed
        ("completed", "completed"),
        # event has been removed from group by leader
        ("archived", "archived"),
    )
    status = models.CharField(
        choices=STATUS_CHOICES, blank=True, null=True, max_length=48, default="upcoming")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EventManager()

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['at', ]

    def __str__(self):
        return "%s" % (self.at)

    @property
    def at_date(self):
        return datetime.datetime(self.at)

    @property
    def seconds_until_stage_progress(self):
        if self.status == "upcoming":
            return str((self.at - django.utils.timezone.now()).total_seconds()).split(".", 1)[0]
        return 99

    def stage_description(self, status=None):
        if not status:
            status = self.status

        if status == "upcoming":
            return "The group choosing event is scheduled and being prepared."
        if status == "starting":
            return "Get in the lobby now. You will have more control over what's picked."
        if status == "in_progress":
            return "Choices are being made and you aren't there. Join the event now!"
        if status == "vetoing":
            return "The group is vetoing the suggested choices they really don't want."
        if status == "completing":
            return "The group chose a great restaurant."
        return None

    @property
    def next_stage_at(self):
        if self.status == "upcoming":
            return self.at - datetime.timedelta(seconds=self.group.event_starting_seconds)

    @property
    def next_stage(self):
        if self.status == "upcoming":
            return "starting"
        if self.status == "starting":
            return "in_progress"
        if self.status == "in_progress":
            return "vetoing"
        if self.status == "vetoing":
            return "completing"
        if self.status == "completing":
            return "completed"
        return None

    @property
    def next_stage_description(self):
        return self.stage_description(self.next_stage)

# block the creation of having two events scheduled

# @receiver(pre_save, sender=Group)
# def pre_group_save(sender, instance, **kwargs):
#""" making sure the object doesn't have the same code as another group. """
#
# if not instance.id:
# if Group.objects.filter(code=instance.code).exists():
#instance.code = uuid.uuid4().hex[:6].upper()
#
#""" if the object has been created and we haven't checked the code yet. """
# if instance.id and not instance.checked_code:
# if Group.objects.filter(code=instance.code).count() == 1:
#instance.checked_code = True


class LunchMunchProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)
    zipcode = models.CharField(
        blank=True,
        null=True,
        max_length=5)

    favorite_users = models.ManyToManyField(User,
                                            related_name="favorite_users")

    class Meta:
        verbose_name = "LunchMunchProfile"
        verbose_name_plural = "LunchMunchProfiles"

    def get_absolute_url(self):
        return reverse("account", kwargs={"username": self.user.username})

    def __str__(self):
        return "%s" % (self.user.username)

    def has_group(self):
        groups_ = Group.objects.all()
        groups = []
        for group in groups_:
            if self.user in group.users.all():
                return True
        return False

    def groups(self):
        groups_ = Group.objects.all()
        groups = []
        for group in groups_:
            if self.user in group.users.all():
                groups.append(group)
        return groups

    def favorite_user(self, user):
        if not user in self.favorite_users.all():
            self.favorite_users.add(user)
            self.save()
            return True
        return False

    def unfavorite_user(self, user):
        if user in self.favorite_users.all():
            self.favorite_users.remove(user)
            self.save()
            return True
        return False


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        instance.profile = LunchMunchProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class FavoriteRequestManager(models.Manager):
    def by_user(self, user):
        return self.filter(sender=user)

    def to_user(self, user):
        return self.filter(sender=user)


class FavoriteRequest(models.Model):
    sender = models.ForeignKey(User,
                               blank=False,
                               on_delete=models.CASCADE,
                               related_name="favorite_sender")
    receiver = models.ForeignKey(User,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="favorite_receiver")
    message = models.TextField(
        blank=True,
        null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    objects = FavoriteRequestManager()

    class Meta:
        verbose_name = "Favorite Request"
        verbose_name_plural = "Favorite Requests"
        ordering = ['created_at', ]
