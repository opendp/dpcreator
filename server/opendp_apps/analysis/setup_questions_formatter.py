"""
Note: Will need some redoing when dataset_questions and epsilon_questions are "collapsed" into one variable
 - e.g. https://github.com/opendp/dpcreator/issues/440
Translate the depositor setup questions into JSON for use in the release
Example output:
DepositorSetupInfo.dataset_questions
{"radio_best_describes": "notHarmButConfidential", "radio_only_one_individual_per_row": "yes", "radio_depend_on_private_information": "yes"}

DepositorSetupInfo.epsilon_questions
"""
from opendp_apps.analysis import static_vals as astatic


