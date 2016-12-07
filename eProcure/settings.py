"""
Django settings for eProcure project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'rr33#sp1u0@ni+%la+eciph+fjrmb#tvn)ddkykuva8z19up*h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'eProc',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',    
    'rest_framework',
    'crispy_forms',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'eProcure.urls'

WSGI_APPLICATION = 'eProcure.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        # 'NAME': 'eprocure',
        # 'USER': '',
        # 'PASSWORD': '',
        # 'HOST': '',
        # 'PORT': '',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'eProc/templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CRISPY_TEMPLATE_PACK = "bootstrap3"

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

AUTH_USER_MODEL = 'eProc.User'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'xx@gmail.com'
EMAIL_HOST_PASSWORD = 'xxx'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'xx@gmail.com'

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "static", *MEDIA_URL.strip("/").split("/"))


SCALAR = 570
ROLES = (('SuperUser', 'SuperUser'),('Requester', 'Requester'),('Approver', 'Approver'),('Purchaser', 'Purchaser'),('Receiver', 'Receiver'),('Payer', 'Payer'))  
CURRENCIES = (('USD', 'USD'),('INR', 'INR'),)
LOCATION_TYPES = (('Billing', 'Billing'),('Shipping', 'Shipping'), ('HQ', 'HQ'))
COUNTRIES = (('India', 'India'),('USA', 'USA')) 
EXPENSE_TYPES = (('Asset', 'Asset'),('Expense', 'Expense')) 
STATUSES = (
    #### REQUEST Order Items  ####
    ('Open', 'Open'), #new_req
    ('Requested', 'Requested'), #view_req --> approve req
    ('Approved', 'Approved'), #view_po --> approve po
    ('Denied', 'Denied'), #view_po --> deny po
    ('Cancelled', 'Cancelled'), #view_req or #view_po --> cancel po
    ('Ordered', 'Ordered'), #new_po --> create po
    ('Delivered', 'Delivered'), #receive_items
    ('Paid', 'Paid'), # Updated on view_invoice/1 --> ref view_drawdown
    
    #### DRAWDOWN Order Items  ####
    ('Drawdown Requested', 'Drawdown Requested'), #new_drawdown
    ('Drawdown Approved', 'Drawdown Approved'), #view_drawdown
    ('Drawdown Denied', 'Drawdown Denied'), #view_drawdown
    ('Drawdown Cancelled', 'Drawdown Cancelled'), #view_drawdown
    ('Drawdown Completed', 'Drawdown Completed'), #view_drawdown

    #### Requisitions ####
    ('Pending', 'Pending'), #new_req
    # ('Approved', 'Approved'), #view_req 
    # ('Denied', 'Denied'), #view_req 
    # ('Cancelled', 'Cancelled'), #view_req

    #### POs ####
    # ('Pending', 'Pending'), #new_po
    # ('Open', 'Open'), #view_po --> CHANGE TO APPROVED?
    # ('Denied', 'Denied'), #view_po
    # ('Closed', 'Closed'),  #TODO: receive_items --> all items received OR explicit CLOSE button    
    # ('Cancelled', 'Cancelled'), #view_po
    # ('Paid', 'Paid'),  #new_invoice   

    #### Invoices ####
    # ('Pending', 'Pending'), #TODO Update: On invoice creation
    # ('Approved', 'Approved'),  #new_invoice
    # ('Cancelled', 'Cancelled'), #TODO
    # ('Paid', 'Paid'),  #TODO: Updated on view_invoice/1
    
    #### DRAWDOWN  ###
    # ('Pending', 'Pending'), #new_drawdown
    # ('Approved', 'Approved'),  #view_drawdown
    # ('Denied', 'Denied'),  #view_drawdown
    # ('Cancelled', 'Cancelled'), #view_drawdown
    # ('Completed', 'Completed'), #TODO

    #### ALL #### 
    ('Archived', 'Archived'),
)

# Inform settings.py about local_settings.py
try:
    from local_settings import *    
except ImportError:
    pass
