import session from './session';

export default {

    /**
     * Returns a TermsOfUse object, if it is needed for this user, else returns null
     * @param OpenDPUserId
     * @returns {Promise<AxiosResponse<any>>}
     */
    getTermsOfUse(OpenDPUserId) {
        const formData = new FormData();
        formData.append("OpenDPUserId", apiGeneralToken);

        return session.post('/api/terms/', formData);
    }
}