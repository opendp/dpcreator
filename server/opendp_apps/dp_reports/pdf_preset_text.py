from opendp_apps.dp_reports import pdf_utils as putil

# Reference: https://docs.google.com/document/d/1vY7qP23mmfL672l4BJr8m0k2pZ1DmCLF7tXI_CH0agg/edit#
NEGATIVE_VALUE_PARAS = [
    putil.txt_bld_para('Why it happens'),
    putil.txt_reg_para(f'The noise we add comes from a symmetric distribution about zero (discrete laplace).'),
    putil.txt_reg_para(f"This means it's just as likely to draw a noise value that is greater than zero than it is to draw a noise value less than zero."),
    putil.txt_reg("If a count is small, and the noise is negative, then the output may also be negative."),
    putil.txt_reg_para(""),  # spacer
]
"""
# Why it happens
The noise we add comes from a symmetric distribution about zero (discrete laplace).
This means it's just as likely to draw a noise value that is greater than zero than it is to draw a noise value less than zero.
If a count is small, and the noise is negative, then the output may also be negative.
# Why we do it this way
Adding symmetric noise doesn't introduce bias to the output.
This simple approach also gives the most efficient estimator for counts (lowest budget with highest accuracy).
# Level-setting expectations
We want queries on low-count, highly distinctive bins to be inaccurate.
The purpose of the histogram is to get a sense of the magnitude of each bin.
The same noise scale is used on every bin, so the analyst actually gains just as much information when the bin count is low as when the bin count is high.
People tend to consider error in proportion to the bin magnitude,
which makes bins with smaller counts seem more noisy.
It's also easier to see the noise component on zero queries.
# Interpreting negative values
The magnitude of negative counts can give you additional information as to how near to zero or how likely a count is actually zero.
For example, if a released count has large negative magnitude,
then it is relatively more likely to be zero than a count with a small negative magnitude
(you can actually quantify this by integrating the tail of the pdf of the noise distribution, and it's the same thing we do for accuracies).
# What can I do about it?
If negative magnitudes are not useful information to you (they aren't for many people),
then you can replace negative counts with zero.
Keep in mind that this introduces bias.
In the context of the census, this kind of postprocessing would inflate the population counts of rural areas.
A second approach is to simply remove all counts below a given threshold.
Counts with small magnitude should be more inconsequential to the big picture anyways.
In the context of the census, this kind of postprocessing biases the result towards areas with greater populations.
There is a related algorithm, the stability histogram, that does something similar in a principled way,
but it has an additional delta parameter for releasing the category set. (
"""
