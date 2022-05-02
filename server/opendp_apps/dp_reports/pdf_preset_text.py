"""
Text for fixed pages of the DP Release PDF

https://docs.google.com/document/d/1l7PUHxb7gTt395PUCz2PU2sUH4WgvarkfS-YiVQ7uio/edit#heading=h.bl11r5eigoxz
"""
from decimal import Decimal
from opendp_apps.dp_reports import pdf_utils as putil


PARAMETERS_AND_BOUNDS = [
    # putil.txt_bld_para('Parameters, Bounds, and other Definitions'),
    putil.txt_reg_para(f'This section briefly describes the parameters and bounds used within this report. For more in-depth information, please see https://opendp.org/about.'),

    # Differentially Private (DP) Statistics
    putil.txt_bld_para(f'Differentially Private (DP) Statistics', padding_top=10),
    putil.txt_reg_para_pl40(f'To make a DP release, we replace traditional methods to estimate statistics, or estimators, with randomized estimators that have a calibrated noise distribution.'),

    # Min and Max
    putil.txt_bld_para(f'Bounds: Min and Max'),
    putil.txt_reg_para_pl40(f'The data is clamped to be within minimum and maximum bounds in order to limit the influence any one individual has on the query. If these bounds are too tight, the release may be biased, because values outside these bounds are replaced with the nearest bound. On the other hand, if these bounds are too wide, the respective release will have greater variance.'),

    # Scale
    putil.txt_bld_para(f'Scale and Accuracy'),
    putil.txt_reg_para_pl40(f'Scale is amount of noise added to the query. If using the Laplace mechanism, Laplacian noise with variance 2 * scale^2 is added. Accuracy estimates are derived from this noise parameter.'),

    # Error
    putil.txt_bld_para(f'Accuracy/Error'),
    putil.txt_reg_para_pl40(f'The accuracy or error is the greatest a released, noisy value may differ from the input to the noise mechanism, at a given confidence level. A key observation is that this is not the greatest the DP release may differ from the respective non-DP statistic.'),
    putil.txt_reg_para_pl40(f'For example, suppose that when calculating a DP Mean for age (in years) using a 95% confidence interval, the accuracy/error is 0.959. This means that here is 95% confidence that the DP Mean will be within 0.959 years of the actual mean age. However as mentioned above, there is a approximately 5% chance that the error will be greater than 0.959 years.'),

    # Confidence Level
    putil.txt_bld_para(f'Confidence Level'),
    putil.txt_reg_para_pl40(f'The actual error of the released values is within the error estimate this percentage of the time. It is necessary to specify this confidence level because the noise distribution is unbounded in magnitude (and yet, still preserves utility, because the likelihood of sampling large noise deviates decreases exponentially in the magnitude).'),

    putil.txt_bld_para(f'Privacy Parameters: Epsilon and Delta'),
    putil.txt_reg_para_pl40(
        f'These quantify the privacy loss incurred by individuals in the dataset. Larger values indicate less privacy.'),

    putil.txt_reg_para(' '),

    putil.txt_bld_para_pl40(f'Epsilon'),
    putil.txt_reg_para_pl40(f'Bounds the greatest multiplicative distance between the probability density on your dataset and the probability density on any neighboring dataset. For example, if a potential output has a probability of .01 of being released on your dataset, that same potential output must have a probability within .01 * exp(+/- epsilon) on any neighboring dataset.'),

    putil.txt_bld_para_pl40(f'Delta'),
    putil.txt_reg_para_pl40(f'The probability that the epsilon bound fails. This is usually chosen to be very small, on the order of 1e-10. Some statistics and noise addition mechanisms require a delta parameter.'),
]

NEGATIVE_VALUES = [
    # Why it happens
    putil.txt_bld_para(f'Why they happen', padding_top=Decimal(10)),
    putil.txt_reg_para(f'The noise we add comes from a symmetric distribution about zero (discrete Laplace). This means it\'s just as likely to draw a noise value that is greater than zero than it is to draw a noise value less than zero.'),
    putil.txt_reg_para(f'If a count is small, and the noise is negative, then the output may also be negative.'),

    putil.txt_bld_para(f'Why we do it this way'),
    putil.txt_reg_para('Adding symmetric noise doesn\'t introduce bias to the output. This simple approach also gives the most efficient estimator for counts (lowest budget with highest accuracy).'),

    putil.txt_bld_para(f'Level-setting expectations'),
    putil.txt_reg_para('We want queries on low-count, highly distinctive bins to be inaccurate. The purpose of the histogram is to get a sense of the magnitude of each bin. The same noise scale is used on every bin, so the analyst actually gains just as much information when the bin count is low as when the bin count is high. People tend to consider error in proportion to the bin magnitude, which makes bins with smaller counts seem more noisy. It\'s also easier to see the noise component on zero queries.'),

    putil.txt_bld_para(f'Interpreting negative values'),
    putil.txt_reg_para('The magnitude of negative counts can give you additional information as to how near to zero or how likely a count is actually zero. For example, if a released count has large negative magnitude, then it is relatively more likely to be zero than a count with a small negative magnitude. (You can actually quantify this by integrating the tail of the pdf of the noise distribution, and it\'s the same thing we do for accuracies.)'),

    putil.txt_bld_para(f'What can I do about it?'),
    putil.txt_reg_para('If negative magnitudes are not useful information to you (they aren\'t for many people), then you can replace negative counts with zero. Keep in mind that this introduces bias. In the context of the census, this kind of postprocessing would inflate the population counts of rural areas.'),
    putil.txt_reg_para('A second approach is to simply remove all counts below a given threshold. In theory, counts with small magnitude should be less consequential to the big picture. In the context of the census, this kind of postprocessing biases the result towards areas with greater populations. There is a related algorithm, the stability histogram, that does something similar in a principled way, but it has an additional delta parameter for releasing the category set.')
    ]
