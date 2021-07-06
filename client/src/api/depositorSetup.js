import session from './session';

export default {

    /**
     *  Updates a DepositSetupInfo object with the properties
     * @param objectId DepositorSetupInfo identifier
     * @param props  the new values to be saved
     * @returns {Promise<AxiosResponse<any>>} the updated object
     */
    patchDepositorSetup(objectId, props) {
        console.log('calling API patch deposit ' + objectId)
        return session.patch('/api/deposit/' + objectId + '/',
            //  {dataset_questions: { question1: false }, status: 'step200'}).catch( (error) => console.log('error'))
            {dataset_questions: {question1: false}, user_step: 'step200'}).catch((error) => console.log('error'))
    },

};
