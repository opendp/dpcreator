""" Module for plot values eg: type, cdf, labl etc"""
from __future__ import print_function
import logging
import numpy as np
import pandas as pd
from scipy import stats

from .col_info_constants import NATURE_NOMINAL, PLOT_BAR, PLOT_CONTINUOUS, INTERVAL_DISCRETE
from .column_info import ColumnInfo
logger = logging.getLogger(__name__)


class PlotValuesUtil(object):
    """ Class to set up for plot values eg: type, cdf, labl etc"""
    def __init__(self, col_series, col_info):
        assert isinstance(col_series, pd.Series), "col_series must be a pandas.Series object"
        assert isinstance(col_info, ColumnInfo), "col_info must be a ColumnInfo object"

        self.plot_values = list()
        #logger.debug("plot values time")
        #self.dataframe = dataframe
        self.col_info = col_info
        self.colname = self.col_info.colname
        self.col_series = col_series
        self.histlimit = 13
        self.output = {}
        self.cdfx = None
        self.cdfy = None

        self.cal_plot_values()
        self.col_info.tidy_plot_values()



    def ecdf(self, data):
        """Compute ECDF for a one-dimensional array of measurements."""
        # Number of data points: size
        raw_data = np.array(self.col_series)

        # x-data for the ECDF: x_
        x_value = np.sort(data)
        size_data = raw_data.size
        # y-data for the ECDF: y
        y_value = []

        for i in x_value:
            temp = raw_data[raw_data <= i]
            val = temp.size / size_data
            y_value.append(val)

        return y_value

    def cal_plot_values(self):
        """Compute all plot values."""

        nat = self.col_info.nature
        my_interval = self.col_info.interval
        self.col_series.dropna(inplace=True)
        if NATURE_NOMINAL != nat:
            #logger.debug("into not nominal %s", self.colname)

            uniques = np.sort(self.col_series.unique())
            lu = len(uniques)

            if lu < self.histlimit:
                # logger.debug("into it %s", self.colname)
                # code for plot values
                self.col_info.plot_type = PLOT_BAR

                for val, cnt in self.col_series.sort_values().value_counts().items():
                    if type(val) is not str:
                        try:
                            self.output[str(val)] = cnt
                        except TypeError:
                            try:
                                self.output[repr(val)] = cnt
                            except TypeError:
                                pass
                self.col_info.plot_values = self.output

                # code for cdf values
                self.cdfx = np.sort(uniques)
                self.col_info.cdf_plot_type = PLOT_BAR
                self.col_info.cdf_plotx = np.linspace(start=min(self.cdfx),
                                                      stop=max(self.cdfx), num=len(self.cdfx))
                self.col_info.cdf_ploty = self.ecdf(self.col_info.cdf_plotx)

            else:
                # code for plot values
                self.col_info.plot_type = PLOT_CONTINUOUS
                # here the code for plotx and ploty comes using r density function
                if self.col_series is not None:
                    kernel = stats.gaussian_kde(self.col_series)
                    x = np.linspace(start=min(self.col_series) - kernel.factor,
                                    stop=max(self.col_series) + kernel.factor, num=50)
                    self.col_info.plotx = x
                    self.col_info.ploty = kernel(x)

                # code for cdf values
                self.col_info.cdf_plot_type = PLOT_CONTINUOUS
                if lu >= 50 or (lu < 50 and my_interval != INTERVAL_DISCRETE):
                    self.col_info.cdf_plotx = np.linspace(start=min(self.col_series),
                                                          stop=max(self.col_series), num=50)

                else:
                    self.col_info.cdf_plotx = np.linspace(start=min(self.col_series),
                                                          stop=max(self.col_series), num=lu)
                self.col_info.cdf_ploty = self.ecdf(self.col_info.cdf_plotx)

        else:
            """Here data nature is not nominal"""
            #logger.debug("into it *******%s", self.colname)
            # code for plot values
            self.col_info.plot_type = PLOT_BAR

            for val, cnt in self.col_series.sort_values().value_counts().items():
                if not isinstance(val, str):
                    try:
                        self.output[str(val)] = cnt
                    except TypeError:
                        try:
                            self.output[repr(val)] = cnt
                        except TypeError:
                            pass
                    del cnt
                else:
                    self.output[str(val)] = cnt

            self.col_info.plot_values = self.output

            # code for cdf values
            self.col_info.cdf_plot_type = None
            self.col_info.cdf_plotx = None
            self.col_info.cdf_ploty = None

        # if metadataflag  !=1
        self.col_info.labl = ""
