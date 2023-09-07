import jsonschema
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck


class SchemaValidator(BasicErrCheck):
    """Validate a JSON schema"""

    def __init__(self, schema_dict, release_info):
        self.schema_dict = schema_dict
        self.release_info = release_info

        self.run_precheck()
        self.validate_schema()

    def run_precheck(self):
        """Check the data before validating"""
        if not isinstance(self.schema_dict, dict):
            self.add_err_msg('Schema data (schema_dict) is not a dict!')
            return

        try:
            jsonschema.Validator.check_schema(self.schema_dict)
        except jsonschema.exceptions.SchemaError as err_obj:
            self.add_err_msg(f'Error in schema: {err_obj.message}')
            return

        if not self.schema_dict:
            self.add_err_msg('Schema data (schema_dict) is empty!')

        if not isinstance(self.release_info, dict):
            self.add_err_msg('Release info (release_info) is not a dict!')
            return

        if not self.release_info:
            self.add_err_msg('Release info (release_info) is empty!')
            return

    def validate_schema(self):
        """Validate the schema"""
        if self.has_error():
            return

        try:
            jsonschema.validate(instance=self.release_info,
                                schema=self.schema_dict)
        except JsonSchemaValidationError as err_obj:
            # import pdb; pdb.set_trace()
            self.add_err_msg(err_obj.message)
            return
