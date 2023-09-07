# Basic settings
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.development_test'
from load_django_settings import *

load_local_settings()

import json
from os.path import abspath, dirname, join
from opendp_apps.release_schemas.schema_validator import SchemaValidator
from opendp_apps.model_helpers.msg_util import msgt

PROJECT_DIR = dirname(dirname(abspath(__file__)))
SCHEMA_DIR = join(dirname(dirname(abspath(__file__))),
                  'opendp_apps', 'release_schemas', 'schemas')
SCHEMA_EXAMPLES_DIR = join(dirname(dirname(abspath(__file__))),
                           'opendp_apps', 'release_schemas', 'testing', 'schema_examples')


def test_schema():
    """Test the schema"""
    schema_file = join(SCHEMA_DIR, 'schema_v0.2.0.json')
    #schema_file = join(SCHEMA_DIR, 'snippet_dpcreator_schema_v01.beta.json')
    schema_example_file = join(SCHEMA_EXAMPLES_DIR, 'release_v0.2.0_test_01.json')

    with open(schema_file, 'r') as in_file:
        schema_dict = json.load(in_file)

    with open(schema_example_file, 'r') as in_file:
        release_info = json.load(in_file)

    validator = SchemaValidator(schema_dict, release_info)
    #validator = SchemaValidator({}, release_info)
    if validator.has_error():
        msgt(f'validator.errors: {validator.get_err_msg()}')
        # print('validator.warnings: ', validator.warnings)
    else:
        print('No errors!')


if __name__ == '__main__':
    test_schema()
