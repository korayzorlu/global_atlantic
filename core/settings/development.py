from .base import *

from decouple import config, Csv

#import sentry_sdk
#import falcon

from dotenv import load_dotenv
load_dotenv()

#DEBUG = config('DEBUG', cast = bool, default = False)
DEBUG = True

#ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default="*,www.micho-app.com,micho-app.com")
ALLOWED_HOSTS = ['*']
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

USE_PG = config('USE_PG', cast = bool, default = False)

if USE_PG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            #'ENGINE': 'django_postgrespool2',
            'NAME': 'postgres',
            'USER': 'micho',
            'PASSWORD': 'Novu.23.PG!',
            'HOST': 'micho-app-db.czrnghcpuvme.eu-central-1.rds.amazonaws.com',
            'PORT': os.getenv("PG_PORT",""),
            "TEST": {
                "NAME": "postgres",
            },
        }
    }
else:
    DATABASES = {
            'default': {
                'ENGINE': 'dj_db_conn_pool.backends.postgresql',
                'NAME': 'globaldb',
                'USER': 'global',
                'PASSWORD': '9527',
                'HOST': 'db',
                'PORT': '5432',
                'POOL_OPTIONS': {
                    'POOL_SIZE': 100,
                    'MAX_OVERFLOW': 50,
                    'RECYCLE': 300
                },
                #'CONN_MAX_AGE': 30, # Bağlantı ömrü (saniye cinsinden)
                "TEST": {
                    "NAME": "globaldb_test",
                },
            }
    }


# DATABASE_POOL_CLASS = 'sqlalchemy.pool.QueuePool'

# DATABASE_POOL_ARGS = {
#     'max_overflow': 10,
#     'pool_size': 200,
#     'recycle': 300,
# }


#This settings for temporary use so they will change in production
# https://data-flair.training/blogs/django-send-email/
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # use this for unreal email sending
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp-mail.outlook.com'
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER","")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD","")
EMAIL_HOST = 'smtp.office365.com'
EMAIL_HOST_USER = "koray.zorlu@novutechnologies.com"
EMAIL_HOST_PASSWORD = "zLR.:786723"
#DEFAULT_FROM_EMAIL = "MichoApp <michoapp@outlook.com>"



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

SECURE_BROWSER_XSS_FILTER = True

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

USE_S3 = config('USE_S3', cast = bool, default = False)

if USE_S3:
    AWS_ACCESS_KEY_ID=""
    AWS_SECRET_ACCESS_KEY=""
    AWS_STORAGE_BUCKET_NAME="michoapp-bucket"
    AWS_S3_REGION_NAME= 'eu-central-1'
    AWS_DEFAULT_ACL= None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    DEFAULT_FILE_STORAGE= 'core.settings.s3utils.PublicMediaStorage'
    STATICFILES_STORAGE= 'core.settings.s3utils.StaticStorage'
    
    STATIC_LOCATION = 'static'
    PUBLIC_MEDIA_LOCATION= "media"
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
else:
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')




#CELERY
# CELERY_IMPORTS = [
#      'tasks',
# ]


CELERY_TIMEZONE = "Europe/Istanbul"
#CELERY_TASK_TRACK_STARTED = True
#CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'

# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

# CELERY_BEAT_SCHEDULE = {
#       'exchange-rates-update': {
#         'task': 'user.tasks.testtask',
#         'schedule': 30.0,
#         'args': '',
#         'options': {
#             'expires': 15.0,
#         },
#     },
# }

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

#SENTRY
# sentry_sdk.init(
#     dsn="https://84f1a0a2445ceab1e79f7828a45c3bdf@o4506433658224640.ingest.sentry.io/4506433660059648",
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )

# api = falcon.API()

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': "channels.layers.InMemoryChannelLayer"
#     }
# }

# CHANNEL_LAYERS= {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#         },
#     },
# }


#rest framework template
CRISPY_TEMPLATE_PACK = "bootstrap4"

