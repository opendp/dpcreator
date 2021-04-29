import session from './session';

export default {
    /**
     * For debugging only TODO: remove when new dataset apis are ready
     * @param apiGeneralToken
     * @param siteUrl
     * @param datasetPid
     * @param fileId
     * @param filePid
     * @returns {Promise<AxiosResponse<any>>}
     */
    getDatasetInfo(apiGeneralToken, siteUrl, datasetPid, fileId, filePid) {
        const formData = new FormData();
        formData.append("apiGeneralToken", apiGeneralToken);
        formData.append("siteUrl", siteUrl);
        formData.append("datasetPid", datasetPid);
        formData.append("fileId", fileId);
        formData.append("filePid", filePid);
        return session.post('/api/dv-dataset/', formData);
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
        console.log('calling API updateDataverseUser ' + openDPUserId + ',' + handoffId)
        return session.post('/api/dv-user/',
            {dv_handoff: handoffId, user: openDPUserId});
    },
    testHandoff(site_url, fileId, datasetPid, token) {
        console.log('posting to dv-handoff')
        const formData = new FormData()
        formData.append("site_url", site_url)
        formData.append("apiGeneralToken", token)
        formData.append('datasetPid', datasetPid)
        formData.append('fileId', fileId)

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
