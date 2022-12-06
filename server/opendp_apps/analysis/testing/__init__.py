"""
docker-compose run server python manage.py test opendp_apps.analysis.testing.test_analysis_plan.AnalysisPlanTest.test_15_create_plan_via_api

docker-compose run server python manage.py test opendp_apps.analysis.testing.test_dp_mean_spec.StatSpecTest.test_40_test_impute

docker-compose run server python manage.py test opendp_apps.analysis.testing.test_dp_histogram_integer_spec.HistogramIntegerStatSpecTest.test_160_run_dphist_int_edges

# Histogram boolean
docker-compose run server python manage.py test opendp_apps.analysis.testing.test_dp_histogram_boolean_spec.HistogramBooleanStatSpecTest

docker-compose run server python manage.py test opendp_apps.analysis.testing.test_dp_histogram_categorical_spec.HistogramCategoricalStatSpecTest.test_130_format_variable_info_categories

docker-compose run server python manage.py test opendp_apps.analysis.testing.test_histogram_util.HistogramUtilTest.test_010_test_int_valid_bins

python manage.py test opendp_apps.analysis.testing.test_dp_count_spec.DPCountStatSpecTest.test_10_valid_spec

python manage.py test opendp_apps.analysis.testing.test_run_release.TestRunRelease.test_10_compute_stats

python manage.py test opendp_apps.analysis.testing.test_dp_histogram_spec.HistogramStatSpecTest.test_105_run_dphist_calculation_categorical

python manage.py test opendp_apps.analysis.testing.test_dp_sum_spec.DPSumStatSpecTest

.test_105_run_dphist_calculation_categorical

python manage.py test opendp_apps.analysis.testing.test_run_release.TestRunRelease.test_90_dp_count_pums_data


"""
