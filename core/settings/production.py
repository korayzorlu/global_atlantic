from .base import *

from decouple import config, Csv

DEBUG = True

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast = Csv())
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'postgres',
            'USER': 'micho',
            'PASSWORD': 'Novu.23.PG!',
            'HOST': 'micho-app-db.czrnghcpuvme.eu-central-1.rds.amazonaws.com',
            'PORT': '5432',
        }
}

#This settings for temporary use so they will change in production
# https://data-flair.training/blogs/django-send-email/
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # use this for unreal email sending
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_HOST_USER = "michoapp@outlook.com"
EMAIL_HOST_PASSWORD = "Michopassword"
DEFAULT_FROM_EMAIL = "Global Atlantic <michoapp@outlook.com>"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

SECURE_BROWSER_XSS_FILTER = True

STATIC_URL = "/static/"
#STATIC_ROOT = os.path.join(BASE_DIR, "static/")
#STATICFILES_DIRS = (
#    os.path.join('static/fonts'),
#    os.path.join('static/images'),
#)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

#AWS_ACCESS_KEY_ID="AKIAXU5U3YQVOQ6IGPVE"
#AWS_SECRET_ACCESS_KEY="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"
#AWS_STORAGE_BUCKET_NAME="michoapp-bucket"
#AWS_S3_REGION_NAME= 'eu-central-1'
#AWS_DEFAULT_ACL= None
#DEFAULT_FILE_STORAGE= 'storages.backends.s3boto3.S3Boto3Storage'
#STATICFILES_STORAGE= 'storages.backends.s3boto3.S3Boto3Storage'



MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#MEDIA_URL = '/mediafiles/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
# MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com//{PUBLIC_MEDIA_LOCATION}/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
