from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from birthdate.models import BirthdateProfile

class Profile(models.Model):
	""" the bridge between auth and non-fundamental data """
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	email = models.EmailField(blank=True, null=True)
	birth_date = models.DateField(null=True, blank=True)

	birthdate_profile = models.ForeignKey(BirthdateProfile, blank=True, null=True, on_delete=models.SET_NULL)

	class Meta:
		verbose_name = "Herriageio Profile"
		verbose_name_plural = "Herriageio Profiles"

	def __str__(self):
		return self.user.username

	def create_birthdate_profile(self):
		# we are saving the profile and not the actual object -- this still
		# saves the respective object -- Same as how we are creating a profile
		# for every user on save
		self.birthdate_profile = BirthdateProfile()
		self.birthdate_profile.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_proile(sender, instance, **kwargs):
    instance.profile.save()

