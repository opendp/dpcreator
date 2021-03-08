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
     *  check if the OpenDPUser is associated with a DataverseUser,
     *  and if so, get the apiToken and siteUrl from the DataverseUser
     *  to call dv-user, and update the DataverseUser with the latest
     *  user info from dataverse.
     *  TODO: update with new API call when ready
     * @param OpenDPUserId
     * @returns {Promise<AxiosResponse<any>>} DataverseUser object
     */
    updateDataverseUser(OpenDPUserId) {
        console.log('calling API updateDataverseUser ' + OpenDPUserId + ',' + siteUrl + ',' + apiGeneralToken)
        const formData = new FormData();
        formData.append("apiGeneralToken", apiGeneralToken);
        formData.append("siteUrl", siteUrl);
        return session.post('/api/dv-user/', formData);
    },
    /**
     * Use token and siteUrl to get Dataverse user info, create DataverseUser object
     * for the OpenDPUser
     * @param OpenDPUserId
     * @param siteUrl
     * @param apiGeneralToken
     * @returns {Promise<AxiosResponse<any>>}  DataverseUser object
     */
    createDataverseUser(OpenDPUserId, siteUrl, apiGeneralToken) {
        console.log('calling API updateDataverseUser ' + OpenDPUserId + ',' + siteUrl + ',' + apiGeneralToken)
        const formData = new FormData();
        formData.append("apiGeneralToken", apiGeneralToken);
        formData.append("siteUrl", siteUrl);
        return session.post('/api/dv-user/', formData);
    }
};
