from ld_similarity_survey.settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c9--1=a9ya2q$lclnrcy@3imnr)5#-18lyxn^my)v6b+k#rq@a'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}