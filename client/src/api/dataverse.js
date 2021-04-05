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
     *  check if there is a DataverseUser for thie openDPUserId and siteUrl.
     *  If there is not create one, else update it with latest info from Dataverse (using handoff object)
     *
     *  TODO: update with new API call when ready
     * @param openDPUserId
     * @param handoffId
     * @returns {Promise<AxiosResponse<any>>} DataverseUser object
     */
    updateDataverseUser(openDPUserId, handoffId) {
        console.log('calling API updateDataverseUser ' + openDPUserId + ',' + handoffId)
        const formData = new FormData()
        formData.append("dataverse_handoff_id", handoffId)
        formData.append("user_id", openDPUserId)
        //   return session.post('/api/dataverses/dv_user/', formData);
        return session.post('/api/dv-user/',
            {dataverse_handoff_id: handoffId, user_id: openDPUserId});
    },

};
