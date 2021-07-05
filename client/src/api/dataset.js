import session from './session';
const camelcaseKeys = require('camelcase-keys');

export default {
    /**
     * Gets a list of datasets that belong to the currently logged in user
     * @returns {Promise<AxiosResponse<any>>}
     */
    getUserDatasets() {
        return session.get('/api/dataset-info/').then(resp => camelcaseKeys(resp, {deep: true}))

    },
    // Gets the DatasetInfo object for the given objectId
    getDatasetInfo(objectId) {
        return session.get('/api/dataset-info/' + objectId + '/').then(resp => camelcaseKeys(resp, {deep: true}))

    }
}