"""
Helpers for updating fields on DepositorSetupInfo
"""
from django.core.exceptions import ValidationError

from opendp_apps.dataset.dataset_question_validators import \
    (validate_dataset_questions,
     validate_epsilon_questions)
from opendp_apps.analysis import static_vals as astatic

def set_user_step_based_on_data(depositor_setup_info) -> None:
    """Based on the data, update the "user_step" field
    @rtype: DepositorSetupInfo object
    """
    assert str(depositor_setup_info._meta) == 'dataset.depositorsetupinfo', \
        "depositor_setup_info must be a DepositorSetupInfo object"

    depositor_setup_info.is_complete = False

    # These error states are should not be changed
    #
    if depositor_setup_info.user_step == depositor_setup_info.DepositorSteps.STEP_9200_DATAVERSE_DOWNLOAD_FAILED:
        return
    if depositor_setup_info.user_step == depositor_setup_info.DepositorSteps.STEP_9300_PROFILING_FAILED:
        return
    if depositor_setup_info.user_step == depositor_setup_info.DepositorSteps.STEP_9400_CREATE_RELEASE_FAILED:
        return

    # Keep updating the user step based on the data available. A bit inefficient, but should
    # stop where data available for that step
    depositor_setup_info.set_user_step(depositor_setup_info.DepositorSteps.STEP_0000_INITIALIZED)
    # depositor_setup_info.set_wizard_step(DepositorSetupInfo.WizardSteps.STEP_0100_FILE_UPLOAD)
    if not depositor_setup_info.get_dataset_info():
        return
    if depositor_setup_info.get_dataset_info().source_file:
        depositor_setup_info.set_user_step(depositor_setup_info.DepositorSteps.STEP_0100_UPLOADED)
        # depositor_setup_info.set_wizard_step(DepositorSetupInfo.WizardSteps.STEP_0200_DATASET_QUESTIONS)
    else:
        return

    if depositor_setup_info.dataset_questions:
        # Dataset questions set, are they valid?
        try:
            validate_dataset_questions(depositor_setup_info.dataset_questions, to_set_user_step=True)
        except ValidationError as _err_obj:
            # They're not valid, don't proceed to the next step
            return
    else:
        # Dataset questions not set, don't proceed to the next step
        return

    if depositor_setup_info.epsilon_questions:
        # Epsilon questions set, are they valid?
        try:
            validate_epsilon_questions(depositor_setup_info.epsilon_questions, to_set_user_step=True)
        except ValidationError as _err_obj:
            # They're not valid, don't proceed to the next step
            return
    else:
        return

    # Dataset questions and epsilon questions are valid, proceed to the next step
    depositor_setup_info.set_user_step(depositor_setup_info.DepositorSteps.STEP_0200_VALIDATED)

    if depositor_setup_info.data_profile:
        depositor_setup_info.set_user_step(depositor_setup_info.DepositorSteps.STEP_0400_PROFILING_COMPLETE)
        # depositor_setup_info.set_wizard_step(DepositorSetupInfo.WizardSteps.STEP_0400_SET_EPSILON)
    else:
        return

    if depositor_setup_info.epsilon:
        depositor_setup_info.set_user_step(depositor_setup_info.DepositorSteps.STEP_0600_EPSILON_SET)
        depositor_setup_info.is_complete = True
    else:
        return

def set_default_epsilon_delta_from_questions(depositor_setup_info) -> None:
    """Based on the data, update the "user_step" field
    @rtype: DepositorSetupInfo object
    """
    assert str(depositor_setup_info._meta) == 'dataset.depositorsetupinfo', \
        "depositor_setup_info must be a DepositorSetupInfo object"

    # Are dataset_questions set and a dict?
    if depositor_setup_info.dataset_questions and isinstance(depositor_setup_info.dataset_questions, dict):
        # Retrieve the answer "key"; see astatic.SETUP_Q_02_ANSWERS
        #
        q2_answer_key = depositor_setup_info.dataset_questions.get(astatic.SETUP_Q_02_ATTR)

        # The setup answer includes the privacy parameters
        #
        setup_answer = astatic.SETUP_Q_02_ANSWERS.get(q2_answer_key)
        if setup_answer and len(setup_answer) == 2:
            _longAnswer, privacy_params = setup_answer  # {'epsilon': .25, 'delta': 10e-6}
            depositor_setup_info.default_epsilon = privacy_params.get('epsilon')
            depositor_setup_info.default_delta = privacy_params.get('delta')
            return

    # Default to None if an answer is not set
    depositor_setup_info.default_epsilon = None
    depositor_setup_info.default_delta = None

