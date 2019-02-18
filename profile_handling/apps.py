from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings


class ProfileHandlingConfig(AppConfig):
    name = 'profile_handling'

    def ready(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            if settings.DEBUG:
                if not User.objects.filter(
                        username=settings.CHANCE_TEST_ADMIN_USERNAME).exists() and not User.objects.filter(
                        username=settings.MASON_TEST_ADMIN_USERNAME).exists():
                    user = User.objects.create_superuser(
                        username=settings.CHANCE_TEST_ADMIN_USERNAME,
                        email="chance@moproblems.io",
                        password=settings.CHANCE_TEST_ADMIN_PASSWORD)
                    user.save()

                    user = User.objects.create_superuser(
                        username=settings.MASON_TEST_ADMIN_USERNAME,
                        email="mason@moproblems.io",
                        password=settings.MASON_TEST_ADMIN_PASSWORD)
                    user.save()
                    print(
                        '[instantiation] [profile_handling] admin accounts created.')
                else:
                    print(
                        '[instantiation] [profile_handling] admin accounts exists.')
            else:
                print(
                    '[instantiation] [profile_handling] admin accounts not created.')
        except Exception as ex:
            print('[instantiation] [profile_handling] objects weren\'t instantiated.')
            print('[instantiation]', str(ex))
