from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp.meas import make_base_laplace
from opendp.mod import binary_search, enable_features
from opendp.trans import \
    (make_bounded_resize,
     make_cast,
     make_clamp,
     make_impute_constant,
     make_select_column,
     make_sized_bounded_mean)

enable_features("floating-point")


class DPMeanInfo(StatSpec):
    """
    Initiate with dict of properties. Example of needed properties:

    spec_props = dict(var_name="hours_sleep",
                      col_index=3,
                      variable_info=dict(min=0, max=24, type=VAR_TYPE_FLOAT),
                      statistic=DP_MEAN,
                      dataset_size=365,
                      epsilon=0.5,
                      ci=CI_95.
                      impute_constant=1)
    """

    def additional_required_props(self):
        """
        Add a list of required properties
        example: ['min', 'max']
        """
        return ['min', 'max', 'ci', 'impute_constant']

    def check_scale(self, scale, preprocessor, dataset_distance, epsilon):
        """
        Return T/F
        :param scale:
        :param preprocessor:
        :param dataset_distance:
        # :param epsilon:
        :return:
        """
        if self.has_error():
            return

        return (preprocessor >> make_base_laplace(scale)).check(dataset_distance, epsilon)

    def get_preprocessor(self):
        """To implement!"""
        if self.has_error():
            return


        preprocessor = (
            # Selects a column of df, Vec<str>
            make_select_column(key=self.col_index, TOA=str) >>
            # Cast the column as Vec<Optional<Float>>
            make_cast(TIA=str, TOA=float) >>
            # Impute missing values to 0 Vec<Float>
            make_impute_constant(self.impute_constant) >>
            # Clamp age values
            make_clamp(self.bounds) >>
            make_bounded_resize(self.dataset_size, self.bounds, self.impute_constant) >>
            make_sized_bounded_mean(self.dataset_size, self.bounds)

            # make_bounded_mean(lower, upper, n=n, T=float)
        )
        return preprocessor
        scale = binary_search(lambda s: self.check_scale(s, preprocessor, 1, self.epsilon),
                              bounds=self.bounds)  #self.bounds)
        preprocessor = preprocessor >> make_base_laplace(scale)
        return preprocessor


