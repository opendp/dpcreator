import session from './session';

const camelcaseKeys = require('camelcase-keys');

export default {

    /**
     * Get the most recent terms of use
     */
    getCurrentTerms() {
        // This will return a list of termsOfAccess, ordered by creation time.
        // We return the first element of the list as the current one

        return session.get('/api/terms-of-access/')
            .then(resp => {
                return camelcaseKeys(resp.data, {deep: true}).results[0]

            })

    },
    /**
     * Returns a history of agreed Terms of Access for this user
     * @param OpenDPUserId
     * @returns {Promise<AxiosResponse<any>>}
     */
    getTermsOfUseLog(OpenDPUserId) {
        return session.get('/api/terms-of-access-agreement/' + OpenDPUserId);
    },
    /**
     *    return session.post('/api/dv-file/',
     {handoff_id: handoffId, creator: openDPUserId})
     .then(resp => camelcaseKeys(resp, {deep: true}))
     * Inserts a row in the termsOfUseAccessLog table, to record user acceptance
     */
    acceptTermsOfUse(user, termsOfAccess) {
        console.log('api user:' + user)
        console.log('api terms:' + termsOfAccess)
        return session.post('/api/terms-of-access-agreement/', {user: user, terms_of_access: termsOfAccess})
    }
}