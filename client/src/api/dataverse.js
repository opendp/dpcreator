import session from './session';

export default {
     getUserInfo(apiGeneralToken, siteUrl) {
         const formData = new FormData();
         formData.append("apiGeneralToken", apiGeneralToken);
         formData.append("siteUrl", siteUrl);
         return session.post('/api/dv-user/', formData);
     },
    getDatasetInfo(apiGeneralToken, siteUrl, datasetPid, fileId, filePid) {
        const formData = new FormData();
        formData.append("apiGeneralToken", apiGeneralToken);
        formData.append("siteUrl", siteUrl);
        formData.append("datasetPid", datasetPid);
        formData.append("fileId", fileId);
        formData.append("filePid", filePid);
        return session.post('/api/dv-dataset/', formData);
    },
    // TODO:
    //  this should call a Django endpoint that will get the
    // user data from Dataverse, create a DataverseUser object in the db,
    // and return the DataverseUser object
    updateDataverseUser(OpenDPUserId, siteUrl, apiGeneralToken) {
        console.log('calling API updateDataverseUser ' + OpenDPUserId + ',' + siteUrl + ',' + apiGeneralToken)
        const formData = new FormData();
        formData.append("apiGeneralToken", apiGeneralToken);
        formData.append("siteUrl", siteUrl);
        return session.post('/api/dv-user/', formData);
    }
};
