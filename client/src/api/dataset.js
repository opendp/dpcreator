import session from './session';
const camelcaseKeys = require('camelcase-keys');

export default {
    /**
     * Gets a list of datasets that belong to the currently logged in user
     *
     */
    getUserDatasets() {
        return session.get('/api/dataset-info/').then(resp => camelcaseKeys(resp, {deep: true}))

    },
    // Gets the DatasetInfo object for the given objectId
    getDatasetInfo(objectId) {
        return session.get('/api/dataset-info/' + objectId + '/').then(resp => camelcaseKeys(resp, {deep: true}))

    },
    runProfiler(datasetId, userId) {
        console.log('posting to profiler....')
        session.post('/api/profile/run-async-profile/',
            {object_id: datasetId})
            .then(resp => camelcaseKeys(resp, {deep: true}))

    }
}