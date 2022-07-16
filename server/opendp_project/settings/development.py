import json
import os

from opendp_project.settings.base import *

DEBUG = True

#PROFILER_DEFAULT_COLUMN_INDICES = json.loads(os.environ.get('PROFILER_DEFAULT_COLUMN_INDICES',
#                                                            '[0, 1, 2, 3, 4, 5, 6]'))

DEFAULT_LOGGER = 'console'

ALLOW_DEMO_LOADING = os.environ.get('ALLOW_DEMO_LOADING', False)
