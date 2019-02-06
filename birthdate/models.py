import django, json, random, uuid

from datetime import datetime, timedelta, date
from dateutil.parser import parse
from smtplib import SMTPException

from django.conf import settings
from django.core import mail, serializers
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse

from .utils import BABY_NAMES

class BirthdateProfile(models.Model):
	""" the information of the user that signed up for birthdate
	
	will contain all the important informaition for this app only.
	
	Extends:
		models.Model
	
	Variables:
		plan_key {[str]} -- use for Stripe plan chargin
		message_credits {[int]} -- [description]
		has_unlimited_credits {bool} -- [description]
		reminder_frequencies {[array]} -- simply set the freuqncy of reminders wtih an array
	"""
	plan_key = models.CharField(blank=True, null=True, max_length=50)

	message_credits = models.PositiveIntegerField(default=0)
	has_unlimited_credits = models.BooleanField(default=False)
	
	reminder_frequencies = models.CharField(default="[1, 5, 30]", max_length=248)

	require_message_send_confirmation = models.BooleanField(default=False)

	class Meta:
		verbose_name = "Birthdate Profile"
		verbose_name_plural = "Birthdate Profiles"

	def __str__(self):
		# we should probably display the most absolute important stat / quick
		# identifier
		return self.message_credits

	@property
	def can_send_message(self):
		if self.has_unlimited_credits or self.message_credits > 0:
			return True
		return False

	@property
	def templates(self):
		# we need to be careful with this method because we don't want to be
		# using too many query calls
		return BirthdateMessageTemplate.objects.filter(author=self)

	def set_reminder_frequencies(self, reminder_frequencies):
		# makes the reminder frequencies ready for the database -- we will
		# pass raw json and this method will take care of the formatting, we
		# don't need to do any of that everytime
		self.reminder_frequencies = json.dumps(reminder_frequencies)

	def get_reminder_frequencies(self):
		return json.loads(self.reminder_frequencies)

class BirthdateContactManager(models.Manager):
	def bulk_import(self, contacts):
		""" bulk import a list of contacts from JSON as that is likely the format
		all temporary contact lists are retrieved
		
		just passes into the raw json files and enumerates and builds the list
		out to create the actual objects one by one
		
		Arguments:
			contacts {BirthdateContact[list]} -- the list of json contacts
		
		Returns:
			[list] -- created list of BirthdateContact objects
		"""
		imported_contacts = []

		for i, contact in enumerate(contacts):
			cur_contact = BirthdateContact.objects.create(**contact)
			imported_contacts.append(cur_contact)

		return imported_contacts

	def compiled_console_str(self, contact):
		contact_console_str = contact.console_str
		messages_contact_str, reminders_contact_str = '', ''

		for message in BirthdateMessage.objects.filter(contact=contact):
			messages_contact_str += '%s\n' %(message.console_str)

		for reminder in BirthdateMessageReminder.objects.for_contact(contact):
			reminders_contact_str += '%s\n' %(reminder.console_str)

		return "\n%s\n%s%s" %(contact.console_str, messages_contact_str, reminders_contact_str)

class BirthdateContact(models.Model):
	def save(self, *args, **kwargs):
		if self.first_name is None and self.email is None and self.nickname is None:
			# cancel the save
			raise Exception('All contacts must have at least one form of name identification.')
			return 
		else:
			super(BirthdateContact, self).save(*args, **kwargs)

	# who we are going to contact
	profile = models.ForeignKey(BirthdateProfile, null=False, blank=False, on_delete=models.CASCADE)
	first_name = models.CharField(blank=False, null=False, max_length=248)
	last_name = models.CharField(blank=True, null=True, max_length=248)
	nickname = models.CharField(blank=True, null=True, max_length=50)
	company = models.CharField(blank=True, null=True, max_length=248)

	# TODO: Connect the automatic retrieval of their birthdays when not supplied
	birthday = models.DateField(blank=True, null=True)

	# TODO: Determine if this would even be needed or wanted
	url = models.CharField(blank=True, null=True, max_length=248)

	# how we are going to contact them
	email = models.EmailField(blank=True, null=True)
	phone_number = models.CharField(blank=True, null=True, max_length=248)
	facebook_key = models.CharField(blank=True, null=True, max_length=248)
	twitter_key = models.CharField(blank=True, null=True, max_length=248)
	linkedin_key = models.CharField(blank=True, null=True, max_length=248)

	notes = models.TextField(blank=True, null=True)

	# we will use the contactsegement as the primary decision factor for the
	# reminder status on add. But we want them to have the option the manually
	# control the reminders for each contact
	reminders_enabled = models.BooleanField(default=True)
	 
	# these will only be changed one-by-one or through list filtering. The
	# segement status changes won't impact these
	reminders_enabled_manually = models.BooleanField(default=False)
	reminders_disabled_manually = models.BooleanField(default=False)

	objects = BirthdateContactManager()

	class Meta:
		verbose_name = "Birthdate Contact"
		verbose_name_plural = "Birthdate Contacts"
		ordering = ['first_name', 'last_name', 'reminders_enabled']

	def __str__(self):
		if self.first_name:
			return self.first_name
		elif self.nickname:
			return self.nickname
		elif self.email:
			return self.email

	@property
	def console_str(self):
		return "%s | %s | %s " %("C", self.upcoming_birthday, self.first_name)

	@property
	def can_have_new_message(self):
		return BirthdateMessage.objects.filter(contact=self, sent=False).count() == 0

	@property
	def active_message(self):
		if self.can_have_new_message:
			return None
		return BirthdateMessage.objects.get(contact=self, sent=False)	

	@property
	def messages(self):
		return BirthdateMessage.objects.filter(contact=self).all()	

	@property
	def current_message(self):
		return BirthdateMessage.objects.filter(contact=self, sent=False).all()

	@property
	def reminder_status_str(self):
		if self.reminders_enabled_manually or self.reminders_enabled:
			return 'enabled'
		return 'disabled'

	@property
	def upcoming_birthday(self):
		upcoming_month = self.birthday.month
		upcoming_day = self.birthday.day

		todays_date = parse(str(date.today().month) + "/" + str(date.today().day) + "/" + str(date.today().year)).date()
		upcoming_date = parse(str(upcoming_month) + "/" + str(upcoming_day) + "/" + str(datetime.today().year)).date()

		# if the date has already passed. Add one year.
		if todays_date > upcoming_date:
			upcoming_date = upcoming_date + timedelta(days=365)

		return upcoming_date

@receiver(pre_save, sender=BirthdateContact)
def create_profile(sender, instance, **kwargs):
	if settings.DEBUG:
		if instance.profile is None:
			instance.profile = BirthdateProfile.objects.create(id=int(Birthdate.profile.objects.count() + 1))
			instance.profile.save()

class BirthdateContactsSegment(models.Model):
	require_unique_template = models.BooleanField(default=False)

	# we will want these here so that we could eventually implement the
	# aspects of forms and API integration so that they could add them to the
	# list that they choose. Public key would be used for sharing, while
	# private would be used for API calls I think
	public_key = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
	private_key = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)

	title = models.CharField(blank=False, null=False, max_length=50)
	contacts = models.ManyToManyField(BirthdateContact)

	# we want booth enabled and disabled for more dynamic control over what we
	# can do.
	reminders_enabled = models.BooleanField(default=True)
	remind_days_before = models.PositiveIntegerField(default=1)

	# TODO:  
	# Implement machine learning options -- we may not really need
	# machine learning and may just be overcomplicating this idea

	class Meta:
		verbose_name = "Birthdate Contacts Segment"
		verbose_name_plural = "Birthdate Contacts Segments"

	def __str__(self):
		return self.title

	def populate_test_contacts(self):
		first_names=(BABY_NAMES)
		i = 0
		while i < 5:
			self.contacts.add(BirthdateContact.objects.create(
				profile=BirthdateProfile.objects.create(id=int(BirthdateProfile.objects.count() + 1)),
				first_name=" ".join(["%s" % (random.choice(first_names)) for _ in range(1)]),
				birthday=parse(str(str(random.randint(1, 12)) + "/" + str(random.randint(1, 28)) + "/" + str(random.randint(1900, 2018))))
				))
			i += 1
		self.save()

	@property
	def reminder_status_str(self):
		if self.reminders_enabled:
			return 'enabled'
		if self.reminders_disabled:
			return 'disabled'
		return 'err_status'

	def enable_reminders(self):
		self.reminders_enabled = True
		self.update_contacts_reminder_statuses('enabled')
		self.save()

	def disable_reminders(self):
		self.reminders_enabled = False
		self.update_contacts_reminder_statuses('disabled')
		self.save()

	def compiled_console_str(self):
		segment_console_str = "%s | %s" %("S", self.title)
		contacts_console_str = ""

		for contact in self.contacts.all().order_by('first_name'):
			contacts_console_str += ".. %s\n" %(contact.console_str)
			for message in BirthdateMessage.objects.filter(contact=contact):
				contacts_console_str += '..%s\n' %(message.console_str)

			for reminder in BirthdateMessageReminder.objects.for_contact(contact):
				contacts_console_str += '..%s\n' %(reminder.console_str)

		return "\n\n%s\n%s" %(segment_console_str, contacts_console_str)

class BirthdateMessageTemplateQuerySet(models.QuerySet):
	def get_random_template(self):
		# i can't believe this actually works -- if we have templates that
		# have a high use count existing then we use that list, but if we
		# don't -- default to the overall public list
		return random.choice(self.filter(private=False, uses__gte=2) or self.filter(private=False)) 

	# TODO:
	# We are going to need a way to build the queryset of the contact
	# information like gender, age, location, friendship time, previous
	# interactions, etc... This option list will need to be completely thought out
	# before we should worry about this though
	# def get_option_matched_template(self):
	# 	pass

class BirthdateMessageTemplate(models.Model):
	public_key = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)

	author = models.ForeignKey(BirthdateProfile, null=False, blank=False, on_delete=models.CASCADE)
	subject = models.CharField(null=False, max_length=50)
	body = models.TextField(null=False)

	uses = models.PositiveIntegerField(default=0)

	# if it's not draft the system can choose this template to send the
	# message with
	draft = models.BooleanField(default=False)
	# if it's not private the system will make it public in the Template
	# marketplace
	private = models.BooleanField(default=False)
	has_been_cloned = models.BooleanField(default=False)
	is_clone = models.BooleanField(default=False)
	cloned_parent_key = models.CharField(blank=True, null=True, max_length=248)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	objects = BirthdateMessageTemplateQuerySet.as_manager()

	class Meta:
		verbose_name = "Birthdate Message Template"
		verbose_name_plural = "Birthdate Message Templates"

	# TODO: We need to create a way to redirect to the view of this template
	# -- this will need to be done when we actually develop the views
	def get_absolute_url(self):
		return reverse('birthdate_template', public_key=self.public_key)

	def get_parent_absolute_url(self):
		return reverse('birthdate_template', public_key=self.cloned_parent_key)

	def __str__(self):
		# returns what we treat as the call line
		return self.subject

	def attribute_use(self, uses_attributing=1):
		self.uses += uses_attributing
		self.save()

	def clone(self, new_author):
		self.has_been_cloned 		= True
		self.attribute_use()

		template_ 					= self
		template_.pk 				= None
		template_.author 			= new_author
		template_.uses 				= 0
		template_.private 			= True
		template_.has_been_cloned 	= False
		template_.is_clone 			= True
		template_.cloned_parent_key = self.public_key
		template_.save()

		return template_

class BirthdateMessage(models.Model):
	template = models.ForeignKey(BirthdateMessageTemplate, null=True, blank=True, on_delete=models.SET_NULL)
	profile = models.ForeignKey(BirthdateProfile, null=False, blank=False, on_delete=models.CASCADE)
	contact = models.ForeignKey(BirthdateContact, null=False, blank=False, on_delete=models.CASCADE)

	# status related info
	draft = models.BooleanField(default=False)
	sent = models.BooleanField(default=False)
	sent_at = models.DateTimeField(default=None, blank=True, null=True)

	future_messages_scheuled = models.BooleanField(default=False) 
	reminders_scheduled = models.BooleanField(default=False)

	# date and time releated info
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	# sending timeline handling
	scheduled_for = models.DateField(blank=False, null=False)

	class Meta:
		verbose_name = "Message"
		verbose_name_plural = "Messages"
		ordering = ['scheduled_for']

	def __str__(self):
		return self.template.subject

	@property
	def console_str(self):
		return ".. %s | %s" %("M", self.scheduled_for)

	def send_message(self):
		print("Dear %s, \n%s\n\n%s" % contact.first_name, template.subject, template.body)
		self.sent = True
		self.sent_at = django.utils.timezone.now()
		self.save()

@receiver(pre_save, sender=BirthdateMessage)
def validate_status_with_template(sender, instance, **kwargs):
	if instance.template is None and instance.sent is False:
		instance.draft = True

@receiver(post_save, sender=BirthdateContact)
def create_first_message(sender, instance, created, **kwargs):
	if created:
		BirthdateMessage.objects.create(
			template=BirthdateMessageTemplate.objects.create(
				author=instance.profile,
				subject="Happy Birthday 🎉🎉🎉", 
				body="I hope your birthday is amazing and special."),
			profile=instance.profile,
			contact=instance,
			scheduled_for=instance.upcoming_birthday)

# has to be down here since we are using the BirthdateMessageReminderManager
@receiver(post_save, sender=BirthdateMessage)
def create_reminders_on_message_create(sender, instance, created=None, **kwargs):
	if created or not instance.reminders_scheduled:
		if instance.contact.reminder_status_str == 'enabled':
			for remind_days_before in instance.profile.get_reminder_frequencies():
				scheduled_for = instance.contact.upcoming_birthday - timedelta(days=remind_days_before)

				BirthdateMessageReminder.objects.create(
					contact=instance.contact, 
					remind_days_before=remind_days_before, 
					scheduled_for=scheduled_for)
			instance.reminders_scheduled = True
			instance.save()

class BirthdateMessageReminderManager(models.Manager):
	def for_contact(self, contact):
		return self.filter(contact=contact)

	def update_segment_reminder_statuses(self, segment_public_key, status_str):
		segment = BirthdateContactsSegment.objects.get(public_key=segment_public_key)

		if status_str == 'enabled':
			# enabling the reminders for all contacts in the segment that
			# haven't been manually disabled
			segment.reminders_enabled = True
			segment.save()

			for contact in segment.contacts.all():
				if not contact.reminders_disabled_manually:
					self.update_contact_reminder_statuses(contact, status_str, segment_called=True)

		elif status_str == 'disabled':
			# sets the segment reminder status as disabled
			segment.reminders_enabled = False
			segment.save()

			# looop through every contact of the segment
			for contact in segment.contacts.all():
				# if the contact hasn't been manually enabled
				if not contact.reminders_enabled_manually:
					# updat ethe reminder status with the status_str of 'disabled'
					self.update_contact_reminder_statuses(contact, status_str, segment_called=True)

		else:
			raise Exception('A valid reminder status_str must be given to change the status.', status_str)

	def update_contact_reminder_statuses(self, contact, status_str, segment_called=None):
		if status_str == 'enabled':
			if not segment_called:
				contact.reminders_disabled_manually = False
				contact.reminders_enabled = True
				if not segment_called:
					contact.reminders_enabled_manually = True
				contact.save()

			for reminder in self.for_contact(contact):
				reminder.disabled = False
				reminder.save()
		elif status_str == 'disabled': 
			contact.reminders_enabled_manually = False
			contact.reminders_enabled = False

			if not segment_called:			
				contact.reminders_disabled_manually = True
			contact.save()

			for reminder in self.for_contact(contact):
				reminder.disabled = True
				reminder.save()
		else:
			raise Exception('A valid reminder status_str must be given to change the status.', status_str)

class BirthdateMessageReminder(models.Model):
	contact = models.ForeignKey(BirthdateContact, blank=False, null=False, on_delete=models.CASCADE)
	remind_days_before = models.PositiveSmallIntegerField(blank=False, null=False)

	in_the_past = models.BooleanField(default=False)
	disabled = models.BooleanField(default=False)
	sent = models.BooleanField(default=False)

	scheduled_for = models.DateField(blank=False, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	sent_at = models.DateTimeField(default=None, blank=True, null=True)

	objects = BirthdateMessageReminderManager()

	class Meta:
		verbose_name = "Message Reminder"
		verbose_name_plural = "Message Reminders"

	def __str__(self):
		return str(self.scheduled_for)

	@property
	def console_str(self):
		return ".... %s | %s | %s" %("R", self.scheduled_for, self.remind_days_before)
	

#@receiver(pre_save, sender=BirthdateMessageReminder)
#def mark_in_the_past(sender, instance, **kwargs):
	#if date.today() > instance.scheduled_for:
		#instance.in_the_past = True

















































