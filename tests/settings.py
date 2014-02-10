__doc__ = """Minimal django settings to run manage.py test command"""

DATABASES = {
    'default': {
        'ENGINE': 'transaction_hooks.backends.sqlite3',
        'NAME': ':memory:',
        'AUTOCOMMIT': True
    }
}

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

INSTALLED_APPS = ('tests', 'transaction_hooks')
SECRET_KEY = '2f!p&amp;gz%6afg4q=34lq3rceo-guy9z@&amp;pgm=hgq7-f+!$5i04w'
