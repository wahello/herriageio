import os
import sys


def process_commands(cmds, app_name):
    for cmd in cmds:
        os.system(cmd)  # runs the command


def build_commands(app_name):
    cmds = [
        'python3 manage.py startapp %s' % (app_name),
        'mkdir "templates/%s"' % (app_name),
        'touch "templates/%s/base.html"' % (app_name),
        'touch "templates/%s/home.html"' % (app_name),
        'mkdir "static/%s"' % (app_name),
        'mkdir "static/%s/css"' % (app_name),
        'touch "static/%s/css/style.css"' % (app_name),
        'mkdir "static/%s/scss"' % (app_name),
        'touch "static/%s/scss/style.scss"' % (app_name),
        'mkdir "static/%s/js"' % (app_name),
        'touch "static/%s/js/scripts.js"' % (app_name),
        'echo "[MANUAL] add %s to INSTALLED_APPS in base.py"' % (app_name),
        'echo "[MANUAL] add %s to herriageio/hosts.py"' % (app_name),
        'echo "[MANUAL] add %s to hostsconf/routing.py"' % (app_name),
        'echo "[MANUAL] add %s/css & %s/scss to Koala"' % (app_name, app_name),
    ]

    process_commands(cmds=cmds, app_name=app_name)


if __name__ == "__main__":
    app_name = str(sys.argv[1])
    build_commands(app_name)
