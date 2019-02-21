""" This is the profile that will be created for each child_app that a user uses.

Model.Profile """

import uuid
import django

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save, post_save

from django.dispatch import receiver
from django.utils.functional import cached_property

from django_hosts import reverse
from mailchimp3 import MailChimp

User = get_user_model()


class Profile(models.Model):
    """ This is the information that will need to be used for each app. Because the subscription they may have to each solution may change. It is wise that it's completely built out to be robust enuogh from the beginning where we don't have to continually add it to it throughout the development process. """
    # this is the parent app account
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    host = models.CharField(max_length=248, blank=False,
                            null=False, choices=settings.CHILD_APPS)

    stripe_id = models.CharField(max_length=248, blank=True, null=True)
    source_id = models.CharField(max_length=248, blank=True, null=True)

    subscription = models.CharField(max_length=24, blank=True, null=True)
    subscription_expiration = models.DateTimeField(blank=True, null=True)

    referred_by_id = models.UUIDField(default=None, blank=True, null=True)
    referral_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)

    friends = models.ManyToManyField(User, related_name="friends", blank=True)

    added_to_mailchimp = models.BooleanField(default=False)

    @cached_property
    def people_referred(self):
        """ Caching the prooperty so that we don't have to continually query this. """
        return Profile.objects.filter(referred_by_id=self.referral_id)

    @property
    def has_subscription(self):
        """ check if the subscriptioon field isn't None. """
        return self.subscription is not None

    @property
    def has_valid_subscription(self):
        """ check if the subscription is actually valid """
        if self.has_subscription:
            if self.subscription_expiration > django.utils.timezone.now():
                # check that the subscription records are still active from Stripe.
                return True
        return False

    @property
    def mailchimp_get(self):
        """ Returns a logged-in mailchimp client """
        return MailChimp(settings.MAILCHIMP_KEY, settings.MAILCHIMP_LOGIN)

    def mailchimp_add_member_to_list(self, listname):
        """ Takes a listname, checks that the member is not a member of the list, then adds it. """
        client = self.mailchimp_get
        listid = settings.MAILCHIMP_LISTS[listname]
        if not self.mailchimp_member_in_list(listname):
            data = {
                'email_address': self.user.email,
                'status': 'subscribed',
                'merge_fields': {
                    'FNAME': self.user.first_name
                }
            }
            client.lists.members.create(listid, data)

            return True
        return False

    @property
    def mailchimp_lists_get(self):
        """ TEMPORARY - Returns a list of all mailchimp lists """
        client = self.mailchimp_get
        return client.lists.all(get_all=True, fields="lists.name,lists.id")

    def mailchimp_member_in_list(self, listname):
        """ Returns a bool indicating if this member's email address is in the list """
        email = self.user.email
        client = self.mailchimp_get
        results = client.lists.members.all(
            settings.MAILCHIMP_LISTS[listname], get_all=True, fields="members.email_address")
        members = results['members']
        addresses = []
        for m in members:
            addresses.append(m['email_address'])

        return email in addresses

    class Meta:
        """ Managing the way that the Profile is displayed in admin. """
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.host

    def get_absolute_url(self):
        return reverse("home", host=self.host)

    def get_settings_url(self):
        return reverse("settings", host="www",
                       kwargs={"profile_host_name": self.host})


@receiver(post_save, sender=User)
def user_post_create_receiver(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            host='www',  # create a profile for 'www' by default
        )


@receiver(post_save, sender=Profile)
def profile_post_save(sender, instance, **kwargs):
    if not instance.added_to_mailchimp and instance.user.email:
        added = instance.mailchimp_add_member_to_list(instance.host)
        if added:
            instance.added_to_mailchimp = True
            instance.save()
