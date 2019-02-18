import os
import json

from django.core.exceptions import ImproperlyConfigured

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


BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
SECRET_KEY = get_env_var("SECRET_KEY")
DEBUG = get_env_var('DEBUG')

ALLOWED_HOSTS = ["*"]
ADMINS = get_env_var("ADMINS")
MANAGERS = ADMINS

DEFAULT_REDIRECT_URL = '.moproblems.io:8000'
PARENT_HOST = DEFAULT_REDIRECT_URL

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party apps
    'django_hosts',
    'widget_tweaks',
    'crispy_forms',
    'social_django',

    # our apps
    'profile_handling',
    'birthdate',
    'tripweather',
    'lunchmunch',
    'herriageio',
    'notes',
]

MIDDLEWARE = [
    # subdomain routing
    'django_hosts.middleware.HostsRequestMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # subdomaing response routing
    'django_hosts.middleware.HostsResponseMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',

    'herriageio.middleware.UserFieldCompilingMiddleware',
    'herriageio.middleware.GetUserProfiles',
    'herriageio.middleware.HasProfileForSolution',
]

# the home urls access
ROOT_URLCONF = 'herriageio.urls'
ROOT_HOSTCONF = 'herriageio.hosts'
DEFAULT_HOST = 'www'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# how the templates are read -- we always need to update DIRS so that we can
# pull the information correctly
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
            'builtins': [
                'django_hosts.templatetags.hosts_override',
            ]
        },
    },
]

# where the wsgi application is -- This is only ever really changed during staging
WSGI_APPLICATION = 'herriageio.wsgi.application'

# database processing and backend
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db',
    }
}


# password validators -- If I ever have to change these I should be considered a pro
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# time settings
LANGUAGE_CODE = get_env_var('LANGUAGE_CODE')
TIME_ZONE = get_env_var('TIME_ZONE')

DATE_FORMAT = "%m/%d/%Y"
DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',  # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
]

USE_L10N = False
USE_TZ = True

# static files
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]
STATIC_URL = '/static/'
if DEBUG:
    STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "herriageio_scdn")
else:
    STATIC_ROOT = "/home/chanceherriage/herriageio/static"


MEDIA_URL = "/media/"
if DEBUG:
    MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "herriageio_mcdn")
else:
    MEDIA_ROOT = "/home/chanceherriage/herriageio/media"

SESSION_COOKIE_DOMAIN = '.moproblems.io'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = 'login_view'
LOGOUT_URL = 'logout_view'
LOGIN_REDIRECT_URL = 'home'

SOCIAL_AUTH_LOGIN_ERROR_URL = '/settings/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/settings/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

SOCIAL_AUTH_GITHUB_KEY = get_env_var('SOCIAL_AUTH_GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = get_env_var('SOCIAL_AUTH_GITHUB_SECRET')
SOCIAL_AUTH_TWITTER_KEY = get_env_var('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = get_env_var('SOCIAL_AUTH_TWITTER_SECRET')
SOCIAL_AUTH_FACEBOOK_KEY = get_env_var('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = get_env_var('SOCIAL_AUTH_FACEBOOK_SECRET')

CHANCE_TEST_ADMIN_USERNAME = get_env_var('CHANCE_TEST_ADMIN_USERNAME')
CHANCE_TEST_ADMIN_PASSWORD = get_env_var('CHANCE_TEST_ADMIN_PASSWORD')
MASON_TEST_ADMIN_USERNAME = get_env_var('MASON_TEST_ADMIN_USERNAME')
MASON_TEST_ADMIN_PASSWORD = get_env_var('MASON_TEST_ADMIN_PASSWORD')

MAILCHIMP_LOGIN = "moproblems"
MAILCHIMP_KEY = get_env_var("MAILCHIMP_KEY")


CHILD_APPS = (('www', 'www'),
              ('birthdate', 'birthdate'),
              ('lunchmunch', 'lunchmunch'),
              ('tripweather', 'tripweather'))

MAILCHIMP_LISTS = {'www': '01e7b6b065',
                   'birthdate': '0d4adf4d52',
                   'lunchmunch': '05b0bd87c0',
                   'tripweather': 'f24a20cd0e'}
