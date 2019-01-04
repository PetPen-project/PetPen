import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = True
TIME_ZONE = 'Asia/Taipei'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
ALLOWED_HOSTS = ['*']
PORT = '8000'
AUTH = ('user','passwd')
MEDIA_ROOT = 'storage'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "petpen/static"),
    ]

# SASS_PROCESSOR_ROOT = STATIC_ROOT
SASS_PROCESSOR_ROOT = STATICFILES_DIRS[0]

EMAIL_USE_TLS = True
EMAIL_HOST = 'localhost'
# EMAIL_HOST_PASSWORD = 'yourpassword'
EMAIL_PORT = 587
