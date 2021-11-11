"""Module for preprocess structure"""

from collections import OrderedDict
import json
from .np_json_encoder import NumpyJSONEncoder
from .col_info_constants import NUMCHAR_NUMERIC, NUMCHAR_CHARACTER, NATURE_VALUES, NUMCHAR_VALUES, DESCRIPTION_LABEL, \
    NUMCHAR_LABEL, NATURE_LABEL


class ColumnInfo(object):
    """Sets up the expected structure of the whole preprocess output file"""

    # names of ColumnInfo *attributes*, not labels, that are editable
    EDITABLE_COLUMNS = ['labl', 'numchar_val', 'nature', 'location_val', 'time_val']

    def __init__(self, colname):
        """Init with column name"""
        # -------------
        # self data
        # -------------

        self.schema = None
        self.description = None
        self.created = None
        self.preprocess_id = None
        self.data_url = None
        self.format = None
        self.preprocess_version = None
        self.schema_version = None

        # -------------
        # more general
        # -------------
        self.colname = colname
        self.labl = None

        self.valid = None
        self.invalid = None

        # ----------------------
        # Type Guess Info
        # ----------------------
        self.numchar_val = None
        self.default_interval = None
        self.nature = None
        self.location_val = None
        self.location_unit = None
        self.time_val = None
        self.time_unit = None
        self.binary = None

        # set at type util
        self.varnames_sum_stat = None

        # Stats Info
        self.mode = []
        self.freqmode = None
        self.mid = None
        self.fewest = []
        self.freqmid = None
        self.freqfewest = None
        self.median = None
        self.mean = None
        self.max = None
        self.min = None
        self.std_dev = None
        self.herfindahl = None

        self.uniques = None

        self.numchar = None
        self.nature = None
        self.binary = None
        self.interval = None
        self.time = None


        #plot vlaues
        self.plot_values = {}
        self.plot_type = None
        self.plotx = None
        self.ploty = None
        self.cdf_plot_type = None
        self.cdf_plotx = None
        self.cdf_ploty = None

    def is_numeric(self):
        # is this NUMCHAR_NUMERIC?
        return self.numchar_val == NUMCHAR_NUMERIC

    def is_character(self):
        # is this NUMCHAR_CHARACTER?
        return self.numchar_val == NUMCHAR_CHARACTER

    @staticmethod
    def is_valid_nature(val):
        """Check if the nature is valid"""
        return val in NATURE_VALUES

    @staticmethod
    def is_valid_numchar(val):
        """Check if the nature is valid"""
        return val in NUMCHAR_VALUES


    def get_numeric_attribute_names(self):
        """These attributes, when set, are always numeric.  Ex/ mean, median, etc."""

        return  ('invalid', 'valid', 'uniques',
                 'median', 'mean', 'max', 'min',
                 'freqmode', 'freqfewest', 'freqmid',
                 'std_dev', 'herfindahl',
                 'plot_values', 'plotx', 'ploty',
                 'cdf_plotx', 'cdf_ploty')

    def is_numeric_attribute(self, ye_attr_name):
        """Test if the attribute is numeric (or null if not set)"""
        if ye_attr_name in self.get_numeric_attribute_names():
            return True
        return False


    def set_fewest(self, fewest_list):
        """Take up to 5 values that occur the fewest number of times"""
        if fewest_list is None:
            self.fewest = []

        self.fewest = fewest_list[:5]

    def set_mode(self, mode_list):
        """Take up to 5 values that occur the greatest number of times"""
        if mode_list is None:
            self.mode = []

        self.mode = mode_list[:5]

    @staticmethod
    def get_editable_column_labels():
        """Return the labels associated with the editable columns"""
        lookup = ColumnInfo.get_variable_label_lookup()

        editable_list = [lookup.get(varname) for varname in ColumnInfo.EDITABLE_COLUMNS]

        assert not None in editable_list,\
            ('SERIOUS ERROR!! In ColumnInfo, EDITABLE_COLUMNS'
             ' has an attribute that either does not exist or'
             ' doesn\'t have a label')

        return editable_list


    @staticmethod
    def get_variable_label_lookup():
        """Return a lookup consisting of {"variable name": "label name"}
        Exclude variables starting with "default" as in "defaultTime" """

        return {info[1]: info[0]
                for info in ColumnInfo.get_variable_labels()
                if not info[0].startswith('default')}


    @staticmethod
    def get_variable_labels():
        """Set labels for variable output.  List of:

         (label, variable name)

        Example of iterating through to show labels and values:
            ```
            for label, varname in self.get_variable_labels():
                variable_val = self.__dict__.get(varname)
                print('%s: %s' % (label, variable_val))
            ```
        """
        label_list = (
            ('variableName', 'colname'),
            (DESCRIPTION_LABEL, 'labl'),

            (NUMCHAR_LABEL, 'numchar_val'),
            (NATURE_LABEL, 'nature'),

            ('binary', 'binary'),
            ('interval', 'default_interval'),
            ('geographic', 'location_val'),
            ('locationUnit', 'location_unit'),
            ('temporal', 'time_val'),
            ('timeUnit', 'time_unit'),

            ('invalidCount', 'invalid'),
            ('validCount', 'valid'),
            ('uniqueCount', 'uniques'),

            ('median', 'median'),
            ('mean', 'mean'),
            ('max', 'max'),
            ('min', 'min'),

            ('mode', 'mode'),
            ('modeFreq', 'freqmode'),
            ('fewestValues', 'fewest'),
            ('fewestFreq', 'freqfewest'),
            ('midpoint', 'mid'),
            ('midpointFreq', 'freqmid'),

            ('stdDev', 'std_dev'),
            ('herfindahlIndex', 'herfindahl'),

            ('plotValues', 'plot_values'),
            ('pdfPlotType', 'plot_type'),
            ('pdfPlotX', 'plotx'),
            ('pdfPlotY', 'ploty'),
            ('cdfPlotType', 'cdf_plot_type'),
            ('cdfPlotX', 'cdf_plotx'),
            ('cdfPlotY', 'cdf_ploty'),

            )
        # print("-"*20)
        # print(label_list)
        return label_list


    def tidy_plot_values(self):
        """for plot values that are None, set them to None or "NA" """
        attr_names = ('plot_type', 'plotx', 'ploty',
                      'cdf_plot_type', 'cdf_plotx', 'cdf_ploty')

        for pname in attr_names:
            val = self.__dict__.get(pname)
            if val is '' or val is []:
                self.__dict__[pname] = None #NOT_APPLICABLE

        # Next 2 lines need to be fixed in the plot
        # value calculation section

        if self.plotx is None and self.ploty is None:
            self.plot_type = None

        if self.cdf_plotx is None and self.cdf_ploty is None:
            self.cdf_plot_type = None

    def print_values(self):
        """print to screen"""
        print('---- %s ----' % self.colname)
        for label, varname in self.get_variable_labels():
            print('%s: %s' % (label, self.__dict__.get(varname)))

    def as_dict(self, as_string=False):
        """For final output"""
        ordered_dict = OrderedDict()

        for label, varname in self.get_variable_labels():
            ordered_dict[label] = self.__dict__.get(varname)

        if as_string:
            return json.dumps(ordered_dict, cls=NumpyJSONEncoder)

        return ordered_dict

"""
from column_info import ColumnInfo
for item in ColumnInfo.get_variable_labels():
    print (item[0])
"""
