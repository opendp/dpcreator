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
};
