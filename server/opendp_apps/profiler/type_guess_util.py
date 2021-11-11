""" Module for type guessing """
import collections
import re

import numpy as np
import pandas as pd
from pandas.api.types import is_float_dtype, is_numeric_dtype
import pycountry
import us

from .col_info_constants import col_info_constants as col_const
from .format_parser import parse

# allow values like 01.02.03
from ..model_helpers.basic_err_check import BasicErrCheck

date_re = re.compile(r'[\d]+\.[\d]+\.[\d]+')
# filter out values like -3, .1, etc
not_date_re = re.compile(r'-?[.\d]+')

digit_re = re.compile(r'[\d]+')


def match(sample, lookup, threshold):
    """returns list of matches for items in sample or None if num matches below threshold"""
    cnt = sample.count()
    bad_cnt, matches = 0, []
    for x in sample:
        if isinstance(x, str):
            x = x.strip().lower()

        match = lookup(x)
        matches.append(match)
        if not match:
            bad_cnt += 1
            if bad_cnt / cnt > 1 - threshold:
                return

    return matches


months = set('jan january feb february mar march apr april may jun june jul july aug august sep september oct october nov november dec december'.split())
days = set('mon monday tue tuesday wed wednesday thu thursday fri friday sat saturday sun sunday'.split())


def lookup_date(val, year):
    """returns date format where possible or None"""
    if not isinstance(val, str):
        return '%Y' if 1600 <= val <= 2100 else None
    if val in months:
        return '%b' if len(val) == 3 else '%B'
    if val in days:
        return '%a' if len(val) == 3 else '%A'

    ori_val = val
    val = val.replace(',', '/')
    if not date_re.fullmatch(val) and not_date_re.fullmatch(val) and ('.' in val or not len(val) in (4, 6, 8)):
        return

    try:
        _, res_format = parse(ori_val)
        if year:
            if len(val) == 4:
                return '%Y'
            elif len(val) == 2:
                return '%y'
            else:
                pass
        return res_format or '?'
    except:
        pass


def lookup_location(x):
    """returns US state, country, country subdivision, or None"""
    if not isinstance(x, str):
        return

    x = pycountry.remove_accents(x)
    ln = len(x)
    if ln == 1 or digit_re.fullmatch(x) or x in {'male', 'no'}:
        return
    if ln == 2:
        state = us.states.lookup(x.upper(), 'abbr')
        if state:
            return 'US state'

    state = us.states.lookup(x.title(), 'name')
    if state:
        return 'US state'

    try:
        pycountry.countries.lookup(x)
        return 'country'
    except:
        pass

    for sd in pycountry.subdivisions:
        for val in sd._fields.values():
            if val is None:
                continue

            val = pycountry.remove_accents(val.lower())
            for val in val.split(';'):
                if val == x:
                    return 'country subdivision'


class TypeGuessUtil(BasicErrCheck):
    """Check variable types of a dataframe"""
    def __init__(self, col_series, col_info, user_vars=None):
        """Init with a pandas dataframe"""
        assert col_series is not None, "dataframe can't be None"

        self.col_series = col_series
        self.col_info = col_info
        self.col_info.location_val = False
        self.col_info.time_val = False
        self.user_vars = user_vars or {}
        self.binary = False

        # final outout returned
        self.check_types()

    def check_types(self):
        var = self.user_vars.get(self.col_info.colname)
        """check the types of the dataframe"""
        # assert self.colnames, 'self.colnames must have values'

        self.col_info.invalid = int(self.col_series.isnull().sum())
        self.col_info.valid = int(self.col_series.count())

        # Drop nulls...
        self.col_series.dropna(inplace=True)

        self.col_info.binary = col_const.BINARY_YES if len(self.col_series.unique()) == 2 else col_const.BINARY_NO

        cnt = self.col_series.count()
        num_sample = 10
        sample = self.col_series.sample(n=num_sample if cnt >= num_sample else cnt, random_state=1)
        if self.is_not_numeric(self.col_series) or self.is_logical(self.col_series):
            time_unit = self.check_time(sample)
            self.col_info.time_val = bool(time_unit)
            self.col_info.time_unit = time_unit if time_unit != '?' else None
            if not self.col_info.time_val:
                location_unit = self.check_location(sample)
                self.col_info.location_val = bool(location_unit)
                self.col_info.location_unit = location_unit

            self.col_info.numchar_val = col_const.NUMCHAR_CHARACTER
            self.col_info.default_interval = col_const.INTERVAL_DISCRETE
            self.col_info.nature = col_const.NATURE_NOMINAL
        else:
            try:
                series_info = self.col_series.astype('int')
            except ValueError as e:
                self.add_err_msg('Type guess error when converting to int: %s' % e)
                return

            if any(series_info.isnull()):
                # CANNOT REACH HERE B/C NULLS ARE DROPPED!

                self.col_info.numchar_val = col_const.NUMCHAR_CHARACTER
                self.col_info.nature = col_const.NATURE_NOMINAL
                self.col_info.default_interval = col_const.INTERVAL_DISCRETE
            else:
                self.col_info.numchar_val = col_const.NUMCHAR_NUMERIC

                ints = self.col_series.where(lambda x: x is 0 or x % 1 == 0.0)
                if is_float_dtype(self.col_series) and ints.count() != len(self.col_series):
                    self.col_info.default_interval = col_const.INTERVAL_CONTINUOUS
                    self.col_info.nature = self.check_nature(self.col_series, True)
                else:
                    time_unit = self.check_time(sample)
                    self.col_info.time_val = bool(time_unit)
                    self.col_info.time_unit = time_unit if time_unit != '?' else None
                    self.col_info.default_interval = col_const.INTERVAL_DISCRETE
                    self.col_info.nature = self.check_nature(series_info, False)

        if var:
            if self.col_info.time_val != var['temporal']:
                self.col_info.time_val = var['temporal']
            if self.col_info.time_unit != var['timeUnit']:
                self.col_info.time_unit = var['timeUnit']
            if self.col_info.location_val != var['geographic']:
                self.col_info.location_val = var['geographic']
            if self.col_info.location_unit != var['locationUnit']:
                self.col_info.location_unit = var['locationUnit']

            # setting the nature to a bad value can cause the entire preprocess to error; needs work
            return
            # This is unreachable
            # if self.col_info.nature != var['nature']:
            #     self.col_info.nature = var['nature']

    @staticmethod
    def is_not_numeric(var_series):
        """Check if pandas Series is a numeric"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        if var_series.size == 0 or var_series.dtype == 'bool':
            return True

        return not is_numeric_dtype(var_series) or var_series.dropna().empty

    @staticmethod
    def is_logical(var_series):
        """Check if pandas Series contains boolean values"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        # Check the dtype
        #    "bool" - True, clearly logical
        #    "object" - possibly logical that had contained np.Nan
        #    ~anything else~ - False
        if var_series.dtype == 'bool':
            return True
        elif var_series.dtype != 'object':
            return False

        # It's an object. Check if all the values are logical
        logical = {True, False, None, np.nan}
        total = sum(cnt for val, cnt in var_series.value_counts(dropna=False).iteritems() if val in logical)
        return total == var_series.size

    @staticmethod
    def check_nature(data_series, continuous_check):
        """Check the nature of the Series"""
        if continuous_check:
            if data_series.between(0, 1).all():
                return col_const.NATURE_PERCENT
            elif data_series.between(0, 100).all() and min(data_series) < 15 and max(data_series) > 85:
                return col_const.NATURE_PERCENT
            return col_const.NATURE_RATIO
        return col_const.NATURE_ORDINAL

    @staticmethod
    def check_time(var_series):
        """Check if Series is a datetime"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        name = var_series.name.lower()
        if name.endswith('id') or not var_series.dtype in ('int64', 'object'):
            return None

        matches = match(var_series, lambda x: lookup_date(x, name == 'year'), 0.5)
        if matches:
            # Add extra check for %b and %B
            tmp_corpus = collections.Counter(x for x in matches if x).most_common(2)
            if len(tmp_corpus) > 1 and '%b' in tmp_corpus[0][0] and '%B' in tmp_corpus[1][0]:
                return tmp_corpus[1][0]
            return tmp_corpus[0][0]

    @staticmethod
    def check_location(var_series):
        """Check if Series is a location"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        if var_series.dtype != 'object':
            return None

        matches = match(var_series, lambda x: lookup_location(x), 0.5)
        if matches:
            return collections.Counter(x for x in matches if x).most_common(1)[0][0]
