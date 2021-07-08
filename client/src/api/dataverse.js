import session from './session';
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
        return session.post('/api/dv-file/',
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
        return session.post('/api/dv-user/',
            {dv_handoff: handoffId, user: openDPUserId});
    },
    testHandoff(site_url, fileId, datasetPid, filePid, token) {
        const formData = new FormData()
        formData.append("site_url", site_url)
        formData.append("apiGeneralToken", token)
        formData.append('datasetPid', datasetPid)
        formData.append('fileId', fileId)
        formData.append("filePid", filePid)

        session.post('/api/dv-handoff/', formData)
            .then(function (response) {
                window.location = response.request.responseURL; // full URI to redirect to
            })
            .catch((error) => {
                console.log(error)
            })
    },
    getDataverseHandoff(handoffId) {
        return session.get('/api/dv-handoff/', {
            params: {
                object_id: 'xyz'
            }
        })
            .then(function (response) {
                console.log(response);
            })

    }

};
