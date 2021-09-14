import pandas as pd
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp.meas import make_base_laplace
from opendp.mod import binary_search, enable_features
from opendp.trans import \
    (make_bounded_resize,
     make_cast,
     make_clamp,
     make_impute_constant,
     make_select_column,
     make_sized_bounded_mean,
     make_split_dataframe)

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

        scale = binary_search(lambda s: self.check_scale(s, preprocessor, 1, self.epsilon),
                              bounds=self.bounds)  #self.bounds)
        preprocessor = preprocessor >> make_base_laplace(scale)
        return preprocessor


    def create_statistic(self):
        """Create the statistic"""
        if self.has_error():
            return

        # Repeating the validity check...
        if not self.is_valid():
            return

        # Assume this works b/c just tried the is_valid() check
        preprocessor = self.get_preprocessor()

        data = """17, 10.2
                6, 15.3
                24, 6.5
                32, 7
                27, 9
                42, 8.5"""
        parse_dataframe = make_split_dataframe(separator=",",
                                               col_names=[0, 1])

        everything = parse_dataframe >> preprocessor
        print('-' * 40)
        dp_result = everything(data)

        print((f"Epsilon: {self.epsilon}"
               f"\nColumn name: {self.var_name}"
               f"\nColumn index: {self.col_index}"
               f"\nDP Mean: {dp_result}"))




