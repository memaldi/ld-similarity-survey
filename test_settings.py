from ld_similarity_survey.settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p!sx9*!f$6=*$a!p-l1ygs47ef&w*-81t-tcz#pc#=w5^gkq9b'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite3',
    }
}


STATIC_URL = '/static/'

LOGIN_URL='/login'