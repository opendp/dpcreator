"""
Settings for running cypress tests
"""
import os

from opendp_project.settings.base import *

DEBUG = True

ROOT_URLCONF = 'opendp_project.urls_cypress'

ALLOW_CYPRESS_TEST_ENDPOINT = 'cypress-in-ci-endpoint'

