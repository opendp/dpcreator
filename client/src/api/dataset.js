import {session, wrappedSession} from './session';
const camelcaseKeys = require('camelcase-keys');

export default {
    /**
     * Gets a list of datasets that belong to the currently logged in user
     *
     */
    getUserDatasets() {
        return wrappedSession.get('/api/dataset-info/').then(resp => camelcaseKeys(resp, {deep: true}))

    },
    // Gets the DatasetInfo object for the given objectId
    getDatasetInfo(objectId) {
        return wrappedSession.get('/api/dataset-info/' + objectId + '/').then(resp => camelcaseKeys(resp, {deep: true}))

    },
    runProfiler(datasetId, userId) {
        wrappedSession.post('/api/profile/run-async-profile/',
            {object_id: datasetId})
            .then(resp => camelcaseKeys(resp, {deep: true}))

    }
}