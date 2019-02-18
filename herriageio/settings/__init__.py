from .base import *

try:
    # we have to put this in try because this is not passed with version control
    if get_env_var("DEBUG"):
        from .local import *
        print('RUNNING WITH: LOCAL.PY')
except:
    pass

try:
    if get_env_var("STAGING"):
        from .staging import *
        print('RUNNING WITH: STAGING.PY')
except:
    pass


try:
    if not get_env_var("STAGING") and not get_env_var("DEBUG"):
        from .production import *
        print('RUNNING WITH: PRODUCTION.PY')
except:
    pass
