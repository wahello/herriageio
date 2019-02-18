import os
import json

from django.core.exceptions import ImproperlyConfigured

# automatically sets the env variable so all we have to do is make sure that the file is there and all the other env variables will be imported properly.
os.environ['SITE_CONFIG'] = './site_config.json'

# we must have the SITE_CONFIG as an environment variable
with open(os.environ.get('SITE_CONFIG')) as f:
    configs = json.loads(f.read())


# just grabs the variable that's been set withtin SITE_CONFIG variable that has to be declared
def get_env_var(setting, configs=configs):
    try:
        val = configs[setting]
        if val == 'True':
            val = True
        elif val == 'False':
            val = False
        return val
    except KeyError:
        error_msg = "ImproperlyConfigured: Set {0} environment variable".format(
            setting)
        raise ImproperlyConfigured(error_msg)
