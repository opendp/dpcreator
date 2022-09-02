"""Compute binned histogram with known category set"""
from opendp.trans import make_count_by_categories, make_find_bin
from opendp.meas import make_base_discrete_laplace
from opendp.typing import L1Distance, VectorDomain, AllDomain, usize
from opendp.mod import binary_search_chain
edges = [1., 3.14159, 4., 7.]
preprocess = (
    make_find_bin(edges=edges) >>
    make_count_by_categories(categories=list(range(len(edges))), TIA=usize)
)

noisy_histogram_from_dataframe = binary_search_chain(
    lambda s: preprocess >> make_base_discrete_laplace(s, D=VectorDomain[AllDomain[int]]),
    d_in=1, d_out=1.)

assert noisy_histogram_from_dataframe.check(1, 1.)
import numpy as np
data = np.random.uniform(0., 10., size=100)

print(noisy_histogram_from_dataframe(data))

# ----


print('-- test_histogram --')
#
import numpy as np
from opendp.trans import make_count_by_categories, make_find_bin
from opendp.meas import make_base_discrete_laplace
from opendp.typing import L1Distance, VectorDomain, AllDomain, usize
from opendp.mod import binary_search_chain
#
dmin = 18
dmax = 68
edges = [dmin, 30, 43, 56, dmax + 1]
epsilon = 1.
#
preprocess = (
        make_find_bin(edges=edges) >>
        make_count_by_categories(categories=list(range(len(edges))),
                                 TIA=usize))
#
noisy_histogram = binary_search_chain(
    lambda s: preprocess >>
              make_base_discrete_laplace(s, D=VectorDomain[AllDomain[int]]),
    d_in=1,
    d_out=epsilon)
#
#
# Noise?
# print(laplacian_scale_to_accuracy(noisy_histogram, .01))
#
assert noisy_histogram.check(1, epsilon)


data = np.random.randint(22, 68, size=100)
teacher_survey_filepath = join(TEST_DATA_DIR,
                               'teacher_survey',
                               'teacher_survey.csv')
self.assertTrue(isfile(teacher_survey_filepath))
df = pd.read_csv(teacher_survey_filepath)
data = df['age'].tolist()

for x in range(1, 4):
    noisy_hist = noisy_histogram(data)
    print(noisy_hist, type(noisy_hist))
