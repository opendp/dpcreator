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
        const formData = new FormData()
        formData.append("dataverse_handoff_id", handoffId)
        formData.append("user_id", openDPUserId)
        return session.post('/api/dv-user/',
            {dv_handoff: handoffId, user: openDPUserId});
    },
    testHandoff() {
        console.log('posting to dv-handoff')
        session.post('/api/dv-handoff/', {
            site_url: 'http://127.0.0.1:8000/dv-mock-api',
            token: 'shoefly-dont-bother-m3',
            fileId: '2342342',
            datasetPid: 'doi:10.7910/DVN/TEST'

        }).catch((error) => {
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
