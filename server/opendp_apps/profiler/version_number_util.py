"""Update the version number within a preprocess dict"""
from decimal import Decimal
from .col_info_constants import col_info_constants as col_const


class VersionNumberUtil(object):
    """Assist with version numbers"""

    @staticmethod
    def update_version_number(preprocess_json, is_major_version=False):
        """Increment the version number by .1
        If "is_major_update", go to the next whole number, e.g. 1.1 -> 2.0
        """
        assert isinstance(preprocess_json, dict), \
            "preprocess_json must be a dict or OrderedDict"

        try:
            version = Decimal(
                preprocess_json[col_const.SELF_SECTION_KEY][col_const.VERSION_KEY])
        except KeyError as err_obj:
            return False, "version not found: %s" % err_obj

        if is_major_version:
            preprocess_json[col_const.SELF_SECTION_KEY][col_const.VERSION_KEY] = \
                Decimal(int(version + Decimal('1.0')))
        else:
            version += Decimal('.1')
            preprocess_json[col_const.SELF_SECTION_KEY][col_const.VERSION_KEY] = \
                version

        return True, preprocess_json
