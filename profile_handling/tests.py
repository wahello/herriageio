from django.contrib.auth import get_user_model
from django.test import TestCase

from profile_handling.models import Profile

User = get_user_model()


class MailchimpTests(TestCase):
    profile = Profile(
        user=User.objects.get(
            username="chance", email="chance@moproblems.io"))

    def test_addition_on_user_with_email_creation(self):
        pass

    def test_addition_on_user_with_email_now(self):
        pass

    def test_get_client(self, profile=profile):
        self.assertIs(profile.mailchimp_get is not None, True)

    def test_get_lists(self, profile=profile):
        lists = profile.mailchimp_lists_get
        print(lists)
        self.assertIs(lists is not None, True)

    def test_add_member_to_list_based_on_current_member_status_with_list(self, profile=profile):
        should_be_in_list, added = True, False

        if not profile.mailchimp_member_in_list("www"):
            added = profile.mailchimp_add_member_to_list("www")
        else:
            should_be_in_list = False

        self.assertIs(added, should_be_in_list)
