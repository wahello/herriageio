import json

from dateutil.parser import parse

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import (
	BirthdateProfile, 
	BirthdateContactsSegment, BirthdateContact, 
	BirthdateMessageTemplate, BirthdateMessageReminder, BirthdateMessage)

User = get_user_model()

class BirthdateProfileTests(TestCase):
	# create a base profile
	def test_user_has_profile(self):
		# checks the existence of the herriageio profile 
		user = User.objects.create_user(username="test_chance")
		self.assertIs(user.profile is not None, True)

	# create a birthdate profile
	def test_create_birthdate_profile(self):
		user = User.objects.create_user(username="test_chance")
		user.profile.create_birthdate_profile()
		self.assertIs(user.profile.birthdate_profile is not None, True)

	# really the account extension list is limitless to our implementation
	# capability.

	def test_get_facebook_friends(self):
		ACCESS_TOKEN = "EAAfa91Gt8Y4BAGJNkj5IRl43YTtVKdE6nInuvAU8qCtWNw6gJCQg559YHJtluSCjoXEJC0WDZBnBSZATzPMIRVtiV2NRa51tLSgdkuNFFGbPFdJTpcE8EpOJ8KWZCnGptcytTqZCmfDLcp9yXZCkQWEAc5DUZC9PxKON6VXUjvCB10eFPP2bCDIBHNVZCAHSCJ38Fh5SsSmZBwZDZD"
		profile_me_url = "https://graph.facebook.com/v3.2/me?access_token=" + ACCESS_TOKEN
		profile_friends_url = "https://graph.facebook.com/v3.2/me/friends?access_token=" + ACCESS_TOKEN

		import requests
		profile_me = requests.get(profile_me_url).text
		profile_friends = requests.get(profile_friends_url).text
		print(profile_friends)

		self.assertIs(profile_friends is not None, True)


	def test_connect_profile_to_twitter(self):
		# add twitter connection to existing BirthdateProfile
		pass

	def test_facebook_connect_and_create_profile(self):
		# authenticate with facebook and then create user from the information
		# grabbed
		pass

	def test_twitter_connect_and_create_profile(self):
		# authenticate with twitter and then create user from the information
		pass

	def test_multiple_connect_and_create_profile(self):
		# authenticate a user with ever available platform
		pass

class ContactTests(TestCase):
# test the the chains are being created successfully
#	def test_contact_console_str(self):
#		contact = BirthdateContact.objects.create(
#			profile=BirthdateProfile.objects.create(),
#			first_name="Chance",
#			last_name="Herriage",
#			nickname="Chancey",
#			company="Herriageio",
#			birthday=parse("10/23/1997"),
#			email="chanceherriage@yahoo.com",)
#		
#		print(BirthdateContact.objects.compiled_console_str(contact))

	# makes sure we can create a contact with just their first name
	def test_first_name_contact_was_created(self): 
		contact = BirthdateContact.objects.create(
			profile=BirthdateProfile.objects.create(),
			first_name="Chance",
			birthday=parse("10/23/1997"))
		self.assertIs(contact is not None, True)

	# makes sure we can create a base user that has personal information
	def test_personal_info_contact_was_created(self):
		contact = BirthdateContact.objects.create(
			profile=BirthdateProfile.objects.create(),
			first_name="Chance",
			last_name="Herriage",
			nickname="Chancey",
			company="Herriageio",
			birthday=parse("10/23/1997"),
			email="chance@yttu.edu",)
		self.assertIs(contact is not None, True)

	def test_bulk_import_contacts(self):
		contact_list = [
			{"profile": BirthdateProfile.objects.create(), "first_name": "Chance", "email": "chanceherriage@yahoo.com", "birthday": parse("10/23/1997")},
			{"profile": BirthdateProfile.objects.create(), "first_name": "Austin", "email": "austin@yahoo.com", "birthday": parse("9/11/1997")}
		]
		imported_contacts = BirthdateContact.objects.bulk_import(contact_list)
		# making sure that both contacts were successfully uploaded
		self.assertIs(len(imported_contacts) == 2, True)

class ContactsSegmentTests(TestCase):
	def test_segment_creation(self):
		segment = BirthdateContactsSegment.objects.create(title="Best Friends")
		segment.populate_test_contacts()
		print(segment.compiled_console_str())

	def test_segment_reminders_disabling(self):
		# should disable all contacts in the segment and should have everyone
		# marked as disabled since there wasn't one manually enabled prior
		segment = BirthdateContactsSegment.objects.create(title="Worst Friends")
		segment.populate_test_contacts()
		BirthdateMessageReminder.objects.update_segment_reminder_statuses(segment_public_key=segment.public_key, status_str="disabled")

		# make sure that all the contacts reminder statuses are disabled		
		self.assertIs(all(contact.reminder_status_str == 'disabled' for contact in segment.contacts.all()), True)

	def test_segment_reminders_disabling_with_one_enabled(self):
		# should disable all contacts, but oone so we shoudl have a mixed list
		# which is what the assertIs is looking for
		segment = BirthdateContactsSegment.objects.create(title="Worst Friends")
		segment.populate_test_contacts()
		BirthdateMessageReminder.objects.update_contact_reminder_statuses(contact=segment.contacts.first(), status_str='enabled')
		BirthdateMessageReminder.objects.update_segment_reminder_statuses(segment_public_key=segment.public_key, status_str="disabled")

		# make sure that not all the contacts are disabled
		self.assertIs(all(contact.reminder_status_str == 'disabled' for contact in segment.contacts.all()), False)
		# make sure that there is at least one contact reminder status as enabled
		self.assertIs(any(contact.reminder_status_str == 'enabled' for contact in segment.contacts.all()), True)

	def test_segment_reminders_enabling(self):
		# Testing that if we have a list we can mark all reminders as disabled.
		segment = BirthdateContactsSegment.objects.create(title="Worst Friends")
		segment.populate_test_contacts()
		BirthdateMessageReminder.objects.update_segment_reminder_statuses(segment_public_key=segment.public_key, status_str="enabled")

		# make sure that all contacts have the reminder status of enabled
		self.assertIs(all(contact.reminder_status_str == 'enabled' for contact in segment.contacts.all()), True)

	def test_segment_reminders_enabling_with_one_disabled(self):
		# Testing that if we have a list we can mark all reminders as
		# disabled and key the one manually changed as the same value.
		segment = BirthdateContactsSegment.objects.create(title="Worst Friends")
		segment.populate_test_contacts()
		BirthdateMessageReminder.objects.update_contact_reminder_statuses(contact=segment.contacts.first(), status_str='disabled')
		BirthdateMessageReminder.objects.update_segment_reminder_statuses(segment_public_key=segment.public_key, status_str="enabled")

		# make sure that not all of the contacts have the remidner status of enabled
		self.assertIs(all(contact.reminder_status_str == 'enabled' for contact in segment.contacts.all()), False)
		# make sure that there is at least one contact with disabled reminder status
		self.assertIs(any(contact.reminder_status_str == 'disabled' for contact in segment.contacts.all()), True)

class TemplateTests(TestCase):
	def test_template_creation(self):
		self.assertIs(BirthdateMessageTemplate.objects.create(
			author=BirthdateProfile.objects.create(),
			subject="Happy Birthday 🎉🎉🎉", 
			body="I hope your birthday is amazing and special.") is not None, True)

	def test_random__with_no_template_greater_than_two(self):
		BirthdateMessageTemplate.objects.create(
			author=BirthdateProfile.objects.create(),
			subject="Happy Birthday 🎉🎉🎉", 
			body="I hope your birthday is amazing and special.",)
		BirthdateMessageTemplate.objects.create(
			author=BirthdateProfile.objects.create(),
			subject="Wishing You A Great Birthday", 
			body="I hope your birthday is amazing and special.",)

		self.assertIs(BirthdateMessageTemplate.objects.get_random_template() is not None, True)

	def test_random_with_templates_greater_than_threshold(self):
		BirthdateMessageTemplate.objects.create(
			author=BirthdateProfile.objects.create(),
			subject="Happy Birthday 🎉🎉🎉", 
			body="I hope your birthday is amazing and special.",
			uses=19)
		BirthdateMessageTemplate.objects.create(
			author=BirthdateProfile.objects.create(),
			subject="Wishing You A Great Birthday", 
			body="I hope your birthday is amazing and special.",
			uses=21)
		self.assertIs(BirthdateMessageTemplate.objects.get_random_template() is not None, True)

	def test_template_clone(self):
		template = BirthdateMessageTemplate.objects.create(
			author=BirthdateProfile.objects.create(),
			subject="Happy Birthday 🎉🎉🎉", 
			body="I hope your birthday is amazing and special.",
			uses=19)
		self.assertIs(template.clone(BirthdateProfile.objects.create()) is not None, True)

class MessageTests(TestCase):
	def test_block_creation_by_already_created(self):
		contact = BirthdateContact.objects.create(
			profile=BirthdateProfile.objects.create(),
			first_name="Chance",
			last_name="Herriage",
			nickname="Chancey",
			company="Herriageio",
			birthday=parse("12/23/1997"),
			email="chance.herriage@ttu.edu",)

		self.assertIs(contact.can_have_new_message, False)












