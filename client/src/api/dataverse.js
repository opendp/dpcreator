import session from './session';

export default {

    getUserInfo(apiGeneralToken, siteUrl) {
        const formData = new FormData();
        formData.append("apiGeneralToken", apiGeneralToken);
        formData.append("siteUrl", siteUrl);
        return session.post('/dv-test/dv-info/get-user-info/', formData);
    },
};
