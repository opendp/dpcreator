"""
Given a ValidateReleaseUtil object that has computed stat,
build the release dict!
"""
import json
from datetime import datetime as dt

from django.template.loader import render_to_string

from opendp_apps.analysis.models import ReleaseInfo
from opendp_apps.dataset.dataset_formatter import DataSetFormatter
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck


class ReleaseInfoFormatter(BasicErrCheck):

    def __init__(self, release_util):
        """Init with a ValidateReleaseUtil object"""
        self.release_util = release_util
        self.analysis_plan = None   # from release_util.analysis_plan
        self.dataset = None         # from release_util.analysis_plan.dataset

        self.release_dict = {}
        self.check_it()
        self.build_release_data()

    def check_it(self):
        """Make sure the computation has been finished"""
        if self.release_util.has_error():
            self.add_err_msg(self.release_util.get_err_msg())
            return

        stat_list = self.release_util.get_release_stats()
        if not stat_list:
            self.add_err_msg('.get_release_stats() failed!')
            return

        self.analysis_plan = self.release_util.analysis_plan
        self.dataset = self.release_util.analysis_plan.dataset


    def get_readable_datetime(self, dt_obj: dt):
        """
        Format a datetime object
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        tz_str = dt_obj.strftime("%Z")
        if tz_str:
            tz_str= f' {tz_str}'

        readable_str = dt_obj.strftime("%B") + ' ' \
                       + dt_obj.strftime("%d") + ', ' \
                       + dt_obj.strftime("%Y") \
                       + ' at ' + dt_obj.strftime("%H:%M:%S:%f") \
                       + tz_str
        return readable_str

    def get_release_data(self, as_json=False):
        """Return the formatted release"""
        assert not self.has_error(), \
            "Make sure `.has_error() if False` before calling .get_release_data()"

        if as_json is True:
            return json.dumps(self.release_dict, indent=4)

        return self.release_dict



    def build_release_data(self):
        """Build the release!"""
        current_dt = dt.now()

        ds_formatter = DataSetFormatter(self.dataset)
        if ds_formatter.has_error():
            self.add_err_msg(ds_formatter.get_err_msg())
            return
        else:
            dataset_dict = ds_formatter.get_formatted_info()

        self.release_dict = {
            "name": str(self.release_util.analysis_plan),
            "release_url": None,    # via with https://github.com/opendp/dpcreator/issues/34
            "created": {
                "iso": current_dt.isoformat(),
                "human_readable": self.get_readable_datetime(current_dt)
            },
            "application": "DP Creator",
            "application_url": "https://github.com/opendp/dpcreator",
            "differentially_private_library": {
                "name": "OpenDP",
                "url": "https://github.com/opendp/opendp",
                "version": self.release_util.opendp_version,
            },
            "dataset": dataset_dict,
            "statistics": self.release_util.get_release_stats()
        }

        # Error check! Make sure it's serializable as JSON and encodable as bytes!!
        try:
            release_json = json.dumps(self.release_dict)
            release_json.encode()
        except TypeError as err_obj:
            user_msg = 'Failed to convert the Release informaation into JSON. ({err_obj})'
            self.add_err_msg(user_msg)

    @staticmethod
    def get_json_filename(release_info_obj: ReleaseInfo) -> str:
        """
        Format the filename to save to the ReleaseInfo.dp_release_json_file field
        """
        assert release_info_obj.object_id, \
            "Make sure the ReleaseInfo is saved and has an \"object_id\" before calling this method"
        return f'release-{release_info_obj.object_id}.json'

    @staticmethod
    def get_pdf_filename(release_info_obj: ReleaseInfo) -> str:
        """
        Format the filename to save to the ReleaseInfo.dp_release_pdf_file field
        """
        assert release_info_obj.object_id, \
            "Make sure the ReleaseInfo is saved and has an \"object_id\" before calling this method"
        return f'release-{release_info_obj.object_id}.pdf'

    @staticmethod
    def get_tex_filename(release_info_obj: ReleaseInfo) -> str:
        """
        Format the filename to save to the ReleaseInfo.dp_release_pdf_file field
        """
        assert release_info_obj.object_id, \
            "Make sure the ReleaseInfo is saved and has an \"object_id\" before calling this method"
        return f'release-{release_info_obj.object_id}.tex'

    @staticmethod
    def create_release_description_html(release_info_obj: ReleaseInfo=None) -> str:
        """
        Create an HTML description using a ReleaseInfo object
        """
        html_desc = render_to_string('analysis/release_description.html',
                                     {'dp_statistics': release_info_obj.dp_statistics}) #release_info_obj})
        return html_desc

"""
python manage.py shell

from opendp_apps.analysis.release_info_formatter import ReleaseInfoFormatter

some_html = ReleaseInfoFormatter.create_release_description_html()
print(some_html)
"""