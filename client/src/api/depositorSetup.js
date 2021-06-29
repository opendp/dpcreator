import session from './session';

export default {

    /**
     *  check if there is a DataverseFileInfo for this openDPUserId and siteUrl (contained in handoff object).
     *  If there is not create one, else update it with latest info from Dataverse (using handoff object)
     *
     * @param openDPUserId
     * @param handoffId
     * @returns {Promise<AxiosResponse<any>>} DataverseUser object
     */
    patchDepositorSetup(objectId) {
        console.log('calling API patch deposit ' + objectId)
        return session.patch('/api/deposit/' + objectId + '/',
            //  {dataset_questions: { question1: false }, status: 'step200'}).catch( (error) => console.log('error'))
            {dataset_questions: {question1: false}, user_step: 'step200'}).catch((error) => console.log('error'))
    },

};
