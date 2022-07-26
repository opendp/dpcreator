"""
Note: Will need some redoing when dataset_questions and epsilon_questions are "collapsed" into one variable
 - e.g. https://github.com/opendp/dpcreator/issues/440
Translate the depositor setup questions into JSON for use in the release
Example output:
- DepositorSetupInfo.dataset_questions
- {"radio_best_describes": "notHarmButConfidential",
   "radio_only_one_individual_per_row": "yes",
   "radio_depend_on_private_information": "yes"}

- DepositorSetupInfo.epsilon_questions
- {"secret_sample": "yes",
    "population_size": "1000000",
   "observations_number_can_be_public": "yes"}
"""
from __future__ import annotations

import json

from django.core.serializers.json import DjangoJSONEncoder

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck


class SetupQuestionFormatter(BasicErrCheck):
    """Format the setup questions for use in a release"""

    def __init__(self, depositor_setup_info: DepositorSetupInfo):
        self.dsetup_info = depositor_setup_info
        self.formatted_questions = []

        self.format_info()

    def format_info(self):
        if self.has_error():
            return

        setup_questions = {}
        if self.dsetup_info.dataset_questions:
            setup_questions = dict(setup_questions, **self.dsetup_info.dataset_questions)

        if self.dsetup_info.epsilon_questions:
            setup_questions = dict(setup_questions, **self.dsetup_info.epsilon_questions)

        qnum = 0
        for qattr in astatic.SETUP_QUESTION_LIST:
            qnum += 1
            if qattr in setup_questions:
                val = setup_questions.get(qattr)
            else:
                val = '(not answered)'

            qinfo = astatic.SETUP_QUESTION_LOOKUP.get(qattr)
            if qinfo:
                qtext, qcontext = astatic.SETUP_QUESTION_LOOKUP.get(qattr)
            else:
                qtext = None
                qcontext = None

            info = dict(question_num=qnum,
                        text=qtext,
                        attribute=qattr,
                        answer=val,
                        context=qcontext
                        )

            # Population size also given, add it to the info dict
            if qattr == astatic.SETUP_Q_02_ATTR:
                setup_answer = astatic.SETUP_Q_02_ANSWERS.get(val)
                if setup_answer and len(setup_answer) == 2:
                    info['longAnswer'], info['privacy_params'] = setup_answer

            if qattr == astatic.SETUP_Q_04_ATTR and val == 'yes':
                info[astatic.SETUP_Q_04a_ATTR] = setup_questions.get(astatic.SETUP_Q_04a_ATTR)

            self.formatted_questions.append(info)

    def as_json(self):
        if self.has_error():
            return None

        return json.dumps(self.formatted_questions, cls=DjangoJSONEncoder, indent=4)

    def as_dict(self):
        if self.has_error():
            return None

        return self.formatted_questions
