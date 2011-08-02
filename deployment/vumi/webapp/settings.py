DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql_psycopg2',  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME':     'vumi',                 # Or path to database file if using sqlite3.
        'USER':     'vumi',                 # Not used with sqlite3.
        'PASSWORD': 'vumi',                 # Not used with sqlite3.
        'HOST':     'localhost',            # Set to empty string for localhost. Not used with sqlite3.
        'PORT':     '',                     # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {'autocommit': True,}
    }
}
