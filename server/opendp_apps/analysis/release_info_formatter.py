"""
Given a ValidateReleaseUtil object that has computed stat,
build the release dict!
"""
from datetime import datetime as dt
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck


class ReleaseInfoFormatter(BasicErrCheck):

    def __init__(self, release_util):
        """Init with a ValidateReleaseUtil object"""
        self.release_util = release_util
        self.release_dict = {}
        self.check_it()

    def check_it(self):
        """Make sure the computation has been finished"""
        if self.release_util.has_error():
            self.add_err_msg(self.release_util.get_err_msg())
            return

        stat_list = self.release_util.get_release_stats()
        if not stat_list:
            self.add_err_msg('.get_release_stats() failed!')
            return

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
        """Return the release!"""
        current_dt = dt.now()

        self.release_dict = \
        {
            "name": str(self.release_util.analysis_plan),
            "release_url": '(not available, should be url within DP Creator)',
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
            "dataset": {
                "dataverse": {
                    "release_deposit_info": {
                        "deposited": True,
                        "dv_urls_to_release": {
                            "release_json": "http://dataverse.edu/some.json",
                            "release_pdf": "http://dataverse.edu/some.pdf"
                        }
                    },
                    "installation": {
                        "name": "(This is static! Fix !) Harvard Dataverse",
                        "dataverse_url": "(This is static! Fix !) https://dataverse.harvard.edu"
                    },
                    "dataset_name": "(This is static! Fix !) Replication data for: The Supreme Court During Crisis: How War Affects Only Nonwar Cases",
                    "file_information(This is static! Fix !) ": {
                        "name": "(This is static! Fix !) crisis.tab",
                        "fileFormat": "text/tab-separated-values",
                        "identifier": "https://doi.org/10.7910/DVN/OLD7MB/ZI4N3J",
                        "description": "Data file for this study"
                    }
                }
            },
            "statistics": self.release_util.get_release_stats()
        }

        return self.release_dict

