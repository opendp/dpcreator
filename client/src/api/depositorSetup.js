import session from './session';

const snakecaseKeys = require('snakecase-keys');


export default {

    /**
     *  Updates a DepositSetupInfo object with the properties
     * @param objectId DepositorSetupInfo identifier
     * @param props  the new values to be saved (json object)
     * @returns {Promise<AxiosResponse<any>>} the updated object
     */
    patchDepositorSetup(objectId, props) {
        const snakeProps = snakecaseKeys(props, {deep: true})
        return session.patch('/api/deposit/' + objectId + '/',
            //  {dataset_questions: { question1: false }, status: 'step200'}).catch( (error) => console.log('error'))
            snakeProps).catch((error) => console.log('error'))
    },

};
