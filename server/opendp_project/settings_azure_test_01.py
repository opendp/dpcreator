import os
from .settings import *

# ----------------------------------
# Azure specific settings
# ----------------------------------
#DEBUG = False
ASGI_APPLICATION = "opendp_project.asgi_azure.application"
