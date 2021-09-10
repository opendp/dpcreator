from opendp.trans import *
from opendp.meas import *

enable_features("floating-point")


def dp_mean(index, lower, upper, n, impute_constant, epsilon):
    """
    Interface to calculate a DP Mean of a column. Note that this does not
    read the data set, this must be done beforehand (see analysis.tests for
    an example)
    :param index:
    :param lower:
    :param upper:
    :param n:
    :param impute_constant:
    :param epsilon:
    :return:
    """

    def check_scale(scale, preprocessor, dataset_distance, epsilon):
        """
        Return T/F
        :param scale:
        :param preprocessor:
        :param dataset_distance:
        :param epsilon:
        :return:
        """
        return (preprocessor >> make_base_laplace(scale)).check(dataset_distance, epsilon)

    bounds = (lower, upper)

    preprocessor = (
        # Selects a column of df, Vec<str>
        make_select_column(key=index, TOA=str) >>
        # Cast the column as Vec<Optional<Float>>
        make_cast(TIA=str, TOA=float) >>
        # Impute missing values to 0 Vec<Float>
        make_impute_constant(impute_constant) >>
        # Clamp age values
        make_clamp(bounds) >>
        make_bounded_resize(n, bounds, impute_constant) >>
        make_sized_bounded_mean(n, bounds)

        #make_bounded_mean(lower, upper, n=n, T=float)
    )
    scale = binary_search(lambda s: check_scale(s, preprocessor, 1, epsilon), bounds=(0., 10.))
    preprocessor = preprocessor >> make_base_laplace(scale)
    return preprocessor
