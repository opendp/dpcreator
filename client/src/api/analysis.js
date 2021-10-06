import session from './session';

const camelcaseKeys = require('camelcase-keys');
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
            snakeProps).then(resp => camelcaseKeys(resp.data, {deep: true}))
            .catch((error) => console.log('error'))
    },
    createAnalysisPlan(datasetId) {
        return session.post('/api/analyze/',
            {object_id: datasetId})
            .then(resp => camelcaseKeys(resp.data, {deep: true}))
    },
    getAnalysisPlan(analysisId) {
        return session.get('/api/analyze/' + analysisId + '/')
            .then(resp => camelcaseKeys(resp.data, {deep: true}))
    },
    patchAnalysisPlan(objectId, props) {
        const snakeProps = snakecaseKeys(props, {deep: true})
        return session.patch('/api/analyze/' + objectId + '/',
            snakeProps).catch((error) => console.log('error'))
    },

};
