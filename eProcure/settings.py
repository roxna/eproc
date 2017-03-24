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

# FOR TEST; SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

# FOR PRODUCTION
# DEBUG = False
# ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'eProc',
    'home',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize', #Converts numbers/totals to comma-separated     
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
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',  #to get url_name in base_portal
                'django.contrib.messages.context_processors.messages',
                
                # Custom template processors in processors.py
                'eProc.processors.icons',
                # 'eProc.processors.buyer',                
                'eProc.processors.notifications',
                'eProc.processors.price_alerts',

                'home.processors.contact',
            ],
        },
    },
]

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

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip("/").split("/"))

AUTH_USER_MODEL = 'eProc.User'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER')


COMPANY_NAME = 'eProc'
CONTACT_EMAIL = 'hello@eproc.com'
CONTACT_PHONE = ''

#######################################
#       FILE UPLOAD OPTIONS           #
#######################################

CONTENT_TYPES = ['image', 'text', 'application']
MAX_UPLOAD_SIZE = "2621440" # 2.5MB - 2621440 / 5MB - 5242880 / 10MB - 10485760


#######################################
#          PAYMENTS / STRIPE          #
#######################################
TRIAL_PERIOD_DAYS = 30

STRIPE_TEST_SECRET_KEY = os.environ['STRIPE_TEST_SECRET_KEY']
STRIPE_TEST_PUBLISHABLE_KEY = os.environ['STRIPE_TEST_PUBLISHABLE_KEY']

STRIPE_LIVE_SECRET_KEY = ""
STRIPE_LIVE_PUBLISHABLE_KEY = ""

#######################################
#           PRICE ALERTS              #
#######################################

# QUANDL: https://www.quandl.com/collections/markets/commodities
QUANDL_API_KEY = os.environ.get('QUANDL_API_KEY')

COMMODITIES = (('Steel', 'Steel'),
               ('Iron Ore', 'Iron Ore'))

                      # (Commodity,   Quandl key_code,    unit)
COMMODITIES_DETAILS = ( ('Steel',    'LME/PR_FM',       '$/mt'), 
                        ('Iron Ore', 'ODA/PIORECR_USD', '$/mt'))


#######################################
#       VARIABLES / OPTIONS           #
#######################################

SCALAR = 570
ROLES = (
    ('SuperUser', 'SuperUser'),
    ('Requester', 'Requester'),
    ('Approver', 'Approver'),
    ('Purchaser', 'Purchaser'),
    # ('Controller', 'Controller'),
    ('Receiver', 'Receiver'), 
    ('Inventory Manager', 'Inventory Manager'),
    # ('Branch Manager', 'Branch Manager')
    ('Payer', 'Payer'), #Accounts Payable
)
# Add Controller: http://kb.procurify.com/?st_kb=new-procurify-add-new-users-need-update

CURRENCIES = (('USD', 'USD'),('INR', 'INR'),)
LOCATION_TYPES = (('Billing', 'Billing'),('Shipping', 'Shipping'), ('HQ', 'HQ'))
INDUSTRY_CHOICES = (('Real Estate', 'Real Estate'), ('Manufacturing', 'Manufacturing'), ('Hospitals', 'Hospitals'))
COUNTRIES = (('India', 'India'),('USA', 'USA')) 
EXPENSE_TYPES = (('Asset', 'Asset'),('Expense', 'Expense')) 

# Statuses used by current_status property (OrderItem/DDItem models)
CURRENT_STATUSES = (
    ('Pending', 'Pending'), 
    ('Approved', 'Approved'),
    ('Denied', 'Denied'),
    ('Cancelled', 'Cancelled'),
    # OrderItems only
    ('Ordered Partial', 'Ordered Partial'),
    ('Ordered Complete', 'Ordered Complete'),
    ('Delivered Partial', 'Delivered Partial'),
    ('Delivered Complete', 'Delivered Complete'),
    ('Returned Complete', 'Returned Complete'),
    # DrawdownItems only
    ('Drawndown Partial', 'Drawndown Partial'),
    ('Drawndown Complete', 'Drawndown Complete'),
)
DELIVERED_STATUSES = ['Delivered Partial', 'Delivered Complete']
DRAWDOWN_STATUSES = ['Drawndown Partial', 'Drawndown Complete']


# Statuses used by get_latest_status (StatusLog models)
ITEM_STATUSES = (
    # Common to OrderItems and DrawdownItems
    ('Pending', 'Pending'), 
    ('Approved', 'Approved'),
    ('Denied', 'Denied'),
    ('Cancelled', 'Cancelled'),
    # OrderItems only
    ('Ordered', 'Ordered'),
    ('Delivered', 'Delivered'),
    ('Returned', 'Returned'),
    # DrawdownItems only
    ('Drawndown', 'Drawndown'),
)
DOC_STATUSES = (
    # Reqs/Invoices:    Pending/Approved/Denied/Cancelled
    # POs:              Open/Closed/Cancelled/(Hold??)
    # Drawdowns:        Pending/Approved/Denied/Cancelled/Closed (call_dd)
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Denied', 'Denied'), 
    ('Cancelled', 'Cancelled'),
    ('Open', 'Open'),
    ('Closed', 'Closed'), 
)

SCORES = (
    (1, 'Poor'),
    (2, 'Average'),
    (3, 'Great'),
)
CATEGORIES = (
    ('Cost/Pricing', 'Cost/Pricing'),
    ('Quality', 'Quality'),
    ('Delivery', 'Delivery'),
    ('Terms', 'Terms'),
    ('Responsiveness', 'Responsiveness'),
)


# Inform settings.py about local_settings.py
try:
    from local_settings import *    
except ImportError:
    pass