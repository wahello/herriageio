import json
import os
import sys

from django.conf import settings
from django.contrib.auth import get_user_model

from django_hosts import patterns, host

from herriageio.hosts import host_patterns
from utils.get_env_var import get_env_var

from profile_handling.models import Profile

User = get_user_model()


def process_commands(cmds, app_name):
    for cmd in cmds:
        os.system(cmd)  # runs the command

    # creating the new profiles for the admin users.
    if Profile.objects.filter(host=app_name).count() != 2:
        Profile.objects.create(
            host=app_name, user=User.objects.get(email="chance@moproblems.io"))
        Profile.objects.create(
            host=app_name, user=User.objects.get(email="mason@moproblems.io"))


def build_commands(app_name):
    cmds = []
    cmds += [
        'python3 manage.py startapp %s' % (app_name),
        'mkdir "templates/%s"' % (app_name),
        'touch "templates/%s/base.html"' % (app_name),
        'touch "templates/%s/home.html"' % (app_name),
        'mkdir "templates/%s/css"' % (app_name),
        'touch "templates/%s/css/style.css"' % (app_name),
        'mkdir "templates/%s/scss"' % (app_name),
        'touch "templates/%s/scss/style.scss"' % (app_name),
        'mkdir "templates/%s/js"' % (app_name),
        'touch "templates/%s/js/scripts.js"' % (app_name),
        'echo "[MANUAL] add %s to herriageio/hosts.py"' % (app_name),
        'echo "[MANUAL] add %s to hostsconf/routing.py"' % (app_name),
        'echo "[MANUAL] add %s/css & %s/scss to Koala"' % (app_name, app_name),
        'echo "[MANUAL] add %s to INSTALLED_APPS in base.py"' % (app_name),
    ]

    process_commands(cmds=cmds, app_name=app_name)


if __name__ == "__main__":
    app_name = str(sys.argv[1])
    build_commands(app_name)
