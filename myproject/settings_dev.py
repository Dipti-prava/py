import os
from dotenv import load_dotenv
from .settings import *
from .config.crypt import decrypt, encrypt
ROOT_URLCONF = 'myproject.urls'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env file
load_dotenv()
print("fjdghgdddddd####################")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': decrypt('gAAAAABlweI9LcyDf2Ki5Np5guFH0rfftkdZZgHPz4fU8blUvl088hH2El45YaaQfyHyoa2qDdN0FJ2EB2Ak2zCYFIsqonnz6w=='),
        'USER': decrypt('gAAAAABlweWaD1Mk_nlkG0wvaBuIa-G48suIUEfIolDBamBDlHDYz3BX7C-1mM5owOwgJ20tBx6VMp6H9DWiBn0PTKvJ2Novrw=='),
        'PASSWORD': decrypt('gAAAAABlweXC1Lht6vSWN3YSmZ6eYaVofrh_oLJr5OboyUVZ9rwE-OwfFx4J1YeyThY5vrDMaeRY2lRgRN1ernj2vOvR95KMuA=='),
        # 'NAME': os.getenv('DB_NAME'),
        # 'USER': os.getenv('DB_USER'),
        # 'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5433'
    }
}

# Configure your email backend settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

print("################", os.getenv('EMAIL_HOST_USER'))
print(BASE_DIR)

# uploaded document folder path
MEDIA_ROOT = 'F:\\py\\documents'
MEDIA_URL = '/media/'
