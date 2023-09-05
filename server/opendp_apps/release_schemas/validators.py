import jsonschema
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from packaging.version import Version, InvalidVersion


def validate_json_schema(value):
    """Validate the JSON schema using the Python library jsonschema"""
    try:
        jsonschema.Validator.check_schema(value)
    except jsonschema.exceptions.SchemaError as err_obj:
        raise ValidationError(f'Error in schema: {err_obj.message}')


def validate_semantic_version_number(value):
    """Validate the semanatic version number"""
    try:
        Version(value)
    except InvalidVersion:
        raise ValidationError(
            _("%(value)s is not a valid version"),
            params={"value": value},
        )

def get_sortable_semantic_version(version_number):
    """Return a sortable version of the semantic version"""
    validate_semantic_version_number(version_number)
    #
    v = Version(version_number)
    #
    vparts = [v.major, v.minor, v.micro]
    vnum = 'v'
    for vpart in vparts:
        vnum += '-' + str(vpart).zfill(4)
    #
    return vnum

def format_semantic_version(version_number):
    """Return a sortable version of the semantic version"""
    validate_semantic_version_number(version_number)
    #
    v = Version(version_number)
    #
    return f'{v.major}.{v.minor}.{v.micro}'
