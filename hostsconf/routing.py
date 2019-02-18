from herriageio.middleware import my_local_global


class BirthdateRouter:
    """
    A router to control all database operations on models in the
    birthdate app.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == 'birthdate':
            return 'birthdate_db'
        if model._meta.app_label == 'tripweather':
            return 'tripweather_db'
        if model._meta.app_label == 'lunchmunch':
            return 'lunchmunch_db'
        return 'db'

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label == 'birthdate':
            return 'birthdate_db'
        if model._meta.app_label == 'tripweather':
            return 'tripweather_db'
        if model._meta.app_label == 'lunchmunch':
            return 'lunchmunch_db'
        return 'db'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        return True
        # if obj1._meta.app_label == 'birthdate' or\
        #        obj2._meta.app_label == 'birthdate' or\
        #        obj1._meta.app_label == 'birthdate' and obj2._meta.app_label == 'auth' or\
        #        obj1._meta.app_label == 'auth' and obj2._meta.app_label == 'birthdate' or \
        #        obj1._meta.app_label == 'tripweather' or\
        #        obj2._meta.app_label == 'tripweather' or\
        #        obj1._meta.app_label == 'tripweather' and obj2._meta.app_label == 'auth' or\
        #        obj1._meta.app_label == 'auth' and obj2._meta.app_label == 'tripweather' or \
        #        obj1._meta.app_label == 'lunchmunch' or \
        #        obj2._meta.app_label == 'lunchmunch' or\
        #        obj1._meta.app_label == 'lunchmunch' and obj2._meta.app_label == 'auth' or\
        #        obj1._meta.app_label == 'auth' and obj2._meta.app_label == 'lunchmunch':
        #    return True
        # return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if app_label == 'birthdate':
            return db == 'birthdate_db'
        if app_label == 'tripweather':
            return db == 'tripweather_db'
        if app_label == 'lunchmunch':
            return db == 'lunchmunch_db'
        return 'db'


class MultiAuthRouter(object):
    def db_for_read(self, model, **hints):
        return my_local_global.database_name
