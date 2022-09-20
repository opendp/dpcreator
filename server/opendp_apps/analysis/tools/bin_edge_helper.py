import numpy as np
from django.core.exceptions import ValidationError

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.utils.extra_validators import \
    (validate_int,
     validate_min_max,
     validate_num_bins_against_min_max,
     validate_edge_count_two_or_greater)


class BinEdgeHelper(BasicErrCheck):
    UNCATEGORIZED = 'uncategorized'

    def __init__(self, min_val: int, max_val: int, number_of_bins: int, **kwargs):

        self.min_val = min_val
        self.max_val = max_val
        self.number_of_bins = number_of_bins

        self.bin_edges = None
        self.buckets = None

        self.check_inputs()
        self.make_edges_buckets()

    def check_inputs(self):
        """Basic validation"""
        try:
            validate_int(self.min_val)
        except ValidationError as err_obj:
            self.add_err_msg(f'{err_obj.message} (min)')
            return

        try:
            validate_int(self.max_val)
        except ValidationError as err_obj:
            self.add_err_msg(f'{err_obj.message} (max)')
            return

        try:
            validate_min_max(self.min_val, self.max_val)
        except ValidationError as err_obj:
            self.add_err_msg(err_obj.message)
            return

        try:
            validate_num_bins_against_min_max(self.number_of_bins, self.min_val, self.max_val)
        except ValidationError as err_obj:
            self.add_err_msg(err_obj.message)
            return

    def make_edges_buckets(self):
        """Create edges and buckets"""
        if self.has_error():
            return

        init_edges = np.linspace(self.min_val,
                                 self.max_val,
                                 self.number_of_bins).round().astype(int)

        # Add "1" to the last edge, e.g. make the last edge inclusive of the max
        # Example: [1, 26, 50, 75, 100] -> [1, 26, 50, 75, 101]; e.g. 100 -> 101
        #
        init_edges[-1] = init_edges[-1] + 1

        self.bin_edges = [int(x) for x in init_edges]

        try:
            validate_edge_count_two_or_greater(self.bin_edges)
        except ValidationError as err_obj:
            self.add_err_msg(err_obj.message)
            return

        self.buckets = self.get_display_bins_inclusive()

    def as_json(self) -> {}:
        """Return the result as JSON"""
        assert self.has_error() is False, \
            "Check that .has_error() is False before using this method"

        return {
            "inputs": {
                "min": self.min_val,
                "max": self.max_val,
                "number_of_bins": self.number_of_bins
            },
            "edges": self.bin_edges,
            "buckets": self.buckets,
            "buckets_right_edge_excluded": self.get_display_bins_right_edge_excluded()
        }

    def get_display_bins_inclusive(self) -> list:
        """
        Convert bin edges to bins for display
        Example:
         in: (1, 25, 50, 75, 101]   # Last number is, 101, is to include max in the last range
         out: ["[1, 24]", "[25, 49]", "[50, 74]", "[75, 100]", "unknown"]  # Last number is, 101, to include max in the last range
        @return: list
        """
        if self.has_error():
            return None

        fmt_edges = []
        last_edge = None
        cnt = 0
        for edge in self.bin_edges:
            cnt += 1
            if cnt > 1:
                right_edge = edge - 1
                fmt_edges.append(f'[{last_edge}, {right_edge}]')
            last_edge = edge

        fmt_edges.append(self.UNCATEGORIZED)

        return fmt_edges

    def get_display_bins_right_edge_excluded(self) -> list:
        """
        Convert bin edges to bins for display
        Example:
         in: (1, 25, 50, 75, 101]   # Last number is, 101, is to include max in the last range
         out: ["[1, 25)", "[26, 50)", "[51, 75)", "[76, 101)", "unknown"]  # Last number is, 101, to include max in the last range
        @return: list
        """
        if self.has_error():
            return None

        fmt_edges = []
        last_edge = None
        cnt = 0
        for edge in self.bin_edges:
            cnt += 1
            if cnt > 1:
                if cnt > 2:
                    last_edge += 1
                fmt_edges.append(f'[{last_edge}, {edge})')
            last_edge = edge

        fmt_edges.append(self.UNCATEGORIZED)

        return fmt_edges


"""
from opendp_apps.analysis.tools.bin_edge_helper import BinEdgeHelper

beh = BinEdgeHelper(0, 100, 5)
if beh.has_error():
    print(beh.get_err_msg())
else:
    print(beh.as_json())
"""
