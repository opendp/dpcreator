"""
Given a ValidateReleaseUtil object that has computed stat,
build the release dict!
"""
from datetime import datetime as dt

from opendp_apps.dataset.models import DataSetInfo
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

    def get_release_data(self):
        """Return the formatted release"""
        assert not self.has_error(), \
            "Make sure `.has_error() if False` before calling .get_release_data()"
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
            "release_url": None,    # to do...
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

