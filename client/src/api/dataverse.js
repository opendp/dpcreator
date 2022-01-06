import {session, wrappedSession} from './session';
const camelcaseKeys = require('camelcase-keys');

export default {

    /**
     *  check if there is a DataverseFileInfo for this openDPUserId and siteUrl (contained in handoff object).
     *  If there is not create one, else update it with latest info from Dataverse (using handoff object)
     *
     * @param openDPUserId
     * @param handoffId
     * @returns {Promise<AxiosResponse<any>>} DataverseUser object
     */
    updateFileInfo(openDPUserId, handoffId) {
        return wrappedSession.post('/api/dv-file/',
            {handoff_id: handoffId, creator: openDPUserId})
            .then(resp => camelcaseKeys(resp, {deep: true}))
    },
    /**
     *  check if there is a DataverseUser for this openDPUserId and siteUrl.
     *  If there is not create one, else update it with latest info from Dataverse (using handoff object)
     *
     * @param openDPUserId
     * @param handoffId
     * @returns {Promise<AxiosResponse<any>>} DataverseUser object
     */
    updateDataverseUser(openDPUserId, handoffId) {
        return wrappedSession.post('/api/dv-user/',
            {dv_handoff: handoffId, user: openDPUserId});
    },
    testHandoff(site_url, fileId, datasetPid, filePid, token) {
        const formData = new FormData()
        formData.append("site_url", site_url)
        formData.append("apiGeneralToken", token)
        formData.append('datasetPid', datasetPid)
        formData.append('fileId', fileId)
        formData.append("filePid", filePid)


        /* INSECURE */
        /* Using the GET endpoint - For testing prior to Dataverse signed urls */
        const asQueryString = new URLSearchParams(formData).toString();
        wrappedSession.get('/api/dv-handoff/dv_orig_create/?' + asQueryString)
            .then(function (response) {
                window.location = response.request.responseURL; // full URI to redirect to
            })


        /* Using the POST endpoint */
        /*
        session.post('/api/dv-handoff/', formData)
            .then(function (response) {
                window.location = response.request.responseURL; // full URI to redirect to
            })
            .catch((error) => {
                console.log(error)
            })
        */
    },
    getDataverseHandoff(handoffId) {
        return wrappedSession.get('/api/dv-handoff/', {
            params: {
                object_id: 'xyz'
            }
        })
            .then(function (response) {
                console.log(response);
            })

    },
    // Gets the DatasetInfo object for the given objectId
    getRegisteredDataverses() {
        return wrappedSession.get('/api/registered-dvs/').then(resp => camelcaseKeys(resp, {deep: true}))

    },

};
