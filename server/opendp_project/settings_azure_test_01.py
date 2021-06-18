import os
from .settings import *

# ----------------------------------
# Azure specific settings
# ----------------------------------
#DEBUG = False
ASGI_APPLICATION = "opendp_project.asgi_azure.application"

# to test...
CORS_ALLOW_ALL_ORIGINS = True

xCORS_ALLOWED_ORIGINS = (
    'http://dev.dpcreator.org',
    'http://52.147.198.81',
    'http://0.0.0.0:8000',
)

# Let nginx serve static files
USE_DEV_STATIC_SERVER = False

STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'static_deploy', 'static', 'dist'))
if not os.path.isdir(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

STATICFILES_DIRS = [
    #os.path.join(BASE_DIR, 'static')
    os.path.join(BASE_DIR, 'static', 'dist')
]